"""
Haven Backend Framework - Durable Active-Record ORM & State Continuity
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
import copy
import time
from haven.continuity import ContinuityLedger, _GLOBAL_LEDGER

T = TypeVar("T", bound="DurableModel")


class Field:
    """Descriptor defining entity schema constraints."""
    def __init__(
        self,
        default: Any = None,
        primary_key: bool = False,
        nullable: bool = False,
        unique: bool = False
    ):
        self.default = default
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.name: Optional[str] = None

    def __set_name__(self, owner: Type, name: str):
        self.name = name


class ModelRegistry:
    """In-memory entity store mapped by model name and primary key."""
    def __init__(self):
        self._stores: Dict[str, Dict[Any, Any]] = {}

    def get_store(self, model_name: str) -> Dict[Any, Any]:
        if model_name not in self._stores:
            self._stores[model_name] = {}
        return self._stores[model_name]

    def clear(self):
        self._stores.clear()


_GLOBAL_REGISTRY = ModelRegistry()


class DurableModelMeta(type):
    """Metaclass extracting schema fields and registering model tables."""
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name == "DurableModel":
            return cls

        fields = {}
        pk_field = "id"

        # Extract type annotations from both cls and namespace
        annotations = {}
        if hasattr(cls, "__annotations__"):
            annotations.update(getattr(cls, "__annotations__", {}))
        annotations.update(namespace.get("__annotations__", {}))

        for field_name in annotations:
            default_val = namespace.get(field_name, None)
            if isinstance(default_val, Field):
                field_obj = default_val
                if field_obj.primary_key:
                    pk_field = field_name
            else:
                field_obj = Field(default=default_val, primary_key=(field_name == "id"))
            fields[field_name] = field_obj

        # Also check class attributes for explicitly declared Fields
        for k, v in namespace.items():
            if isinstance(v, Field) and k not in fields:
                fields[k] = v
                if v.primary_key:
                    pk_field = k

        cls._fields = fields
        cls._pk_field = pk_field
        cls._table_name = name.lower() + "s"
        return cls


class DurableModel(metaclass=DurableModelMeta):
    """
    Active-Record Entity backed by the Open Digital Continuity Standard (ODCS).
    Every entity mutation (create, update, delete) is cryptographically recorded
    into an append-only Merkle ledger, enabling zero-loss recovery and audit replay.
    """
    _fields: Dict[str, Field] = {}
    _pk_field: str = "id"
    _table_name: str = "entities"
    _ledger: Optional[ContinuityLedger] = None

    def __init__(self, **kwargs):
        for k, field in self._fields.items():
            val = kwargs.get(k, field.default)
            setattr(self, k, val)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def pk(self) -> Any:
        return getattr(self, self._pk_field, None)

    @classmethod
    def set_ledger(cls, ledger: ContinuityLedger):
        cls._ledger = ledger

    @classmethod
    def get_ledger(cls) -> ContinuityLedger:
        if cls._ledger is not None:
            return cls._ledger
        return _GLOBAL_LEDGER

    def to_dict(self) -> Dict[str, Any]:
        res = {}
        for k in self._fields:
            val = getattr(self, k, None)
            if hasattr(val, "to_dict") and callable(val.to_dict):
                res[k] = val.to_dict()
            else:
                res[k] = val
        return res

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """Instantiates entity and seals an append-only commit entry in the ledger."""
        instance = cls(**kwargs)
        pk = instance.pk
        if pk is None:
            import uuid
            pk = str(uuid.uuid4())[:8]
            setattr(instance, cls._pk_field, pk)

        store = _GLOBAL_REGISTRY.get_store(cls.__name__)
        store[pk] = instance

        # Record to ODCS Ledger
        payload = {
            "action": "CREATE",
            "model": cls.__name__,
            "pk": pk,
            "data": instance.to_dict(),
            "timestamp": time.time()
        }
        cls.get_ledger().append(payload)
        return instance

    @classmethod
    def find(cls: Type[T], pk: Any) -> Optional[T]:
        """Finds an entity by primary key in O(1) time."""
        store = _GLOBAL_REGISTRY.get_store(cls.__name__)
        return store.get(pk)

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """Returns all entities currently stored."""
        store = _GLOBAL_REGISTRY.get_store(cls.__name__)
        return list(store.values())

    @classmethod
    def filter(cls: Type[T], predicate: Optional[Callable[[T], bool]] = None, **kwargs) -> List[T]:
        """Filters entities by predicate or keyword arguments."""
        items = cls.all()
        if kwargs:
            items = [item for item in items if all(getattr(item, k, None) == v for k, v in kwargs.items())]
        if predicate:
            items = [item for item in items if predicate(item)]
        return items

    @classmethod
    def count(cls) -> int:
        return len(_GLOBAL_REGISTRY.get_store(cls.__name__))

    def update(self, **kwargs) -> 'DurableModel':
        """Mutates entity state and appends cryptographic update receipt to ledger."""
        for k, v in kwargs.items():
            if k in self._fields:
                setattr(self, k, v)

        # Update in-memory
        store = _GLOBAL_REGISTRY.get_store(self.__class__.__name__)
        store[self.pk] = self

        payload = {
            "action": "UPDATE",
            "model": self.__class__.__name__,
            "pk": self.pk,
            "data": self.to_dict(),
            "timestamp": time.time()
        }
        self.get_ledger().append(payload)
        return self

    def delete(self) -> None:
        """Deletes entity and seals tombstone receipt into the Merkle ledger."""
        store = _GLOBAL_REGISTRY.get_store(self.__class__.__name__)
        store.pop(self.pk, None)

        payload = {
            "action": "DELETE",
            "model": self.__class__.__name__,
            "pk": self.pk,
            "timestamp": time.time()
        }
        self.get_ledger().append(payload)

    @classmethod
    def replay_from_ledger(cls: Type[T], ledger: Optional[ContinuityLedger] = None) -> int:
        """
        Reconstructs the entire model table from the cryptographic ledger entries.
        Guarantees 100% deterministic disaster recovery.
        """
        used_ledger = ledger or cls.get_ledger()
        store = _GLOBAL_REGISTRY.get_store(cls.__name__)
        store.clear()

        replayed_count = 0
        for entry in used_ledger.entries:
            p = getattr(entry, "payload", None)
            if p is None and hasattr(entry, "envelope"):
                p = getattr(entry.envelope, "payload", None)
            if isinstance(p, dict) and p.get("model") == cls.__name__:
                action = p.get("action")
                pk = p.get("pk")
                if action in ("CREATE", "UPDATE"):
                    instance = cls(**p.get("data", {}))
                    store[pk] = instance
                    replayed_count += 1
                elif action == "DELETE":
                    store.pop(pk, None)

        return replayed_count

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._fields)
        return f"{self.__class__.__name__}({attrs})"
