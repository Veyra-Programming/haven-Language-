"""
Haven Enterprise Java Concepts Framework
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Implements core Java paradigms:
  1. Interfaces with Default Methods (Interface, @default, @implements)
  2. Sealed Classes and Permits (SealedClass, permits)
  3. Rich Java-style Enums with Fields & Methods (HavenEnum)
  4. Records & Data Carriers (Record)
  5. Generics & Type Bound Constraints (Generic, TypeBound)
"""

import abc
import inspect
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union


# ==============================================================================
# 1. JAVA INTERFACES WITH DEFAULT METHODS
# ==============================================================================

class InterfaceImplementationError(TypeError):
    """Raised when a class fails to implement all required interface methods."""
    pass


class Interface(abc.ABC):
    """
    Java-style Interface base class.
    Methods marked with @abc.abstractmethod must be implemented by implementing classes.
    Methods marked with @default provide default implementations inherited if omitted.
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        for method_name in cls.__abstractmethods__:
            if not any(method_name in B.__dict__ for B in subclass.__mro__):
                return False
        return True


def default(method: Callable) -> Callable:
    """
    Java 'default' interface method:
    Indicates that the interface provides a default fallback implementation.
    """
    setattr(method, "__is_default_method__", True)
    return method


def implements(*interfaces: Type[Interface]):
    """
    Java 'implements InterfaceA, InterfaceB':
    Class decorator that validates complete contract fulfillment at definition time.
    Injects default method implementations from interfaces if not defined on the class.
    """
    def decorator(cls: Type) -> Type:
        cls.__implemented_interfaces__ = interfaces

        # 1. Collect all abstract and default methods from interfaces
        unimplemented = []
        for iface in interfaces:
            if not isinstance(iface, type):
                continue

            # Check all abstract methods
            abstract_methods = getattr(iface, "__abstractmethods__", set())
            for method_name in abstract_methods:
                if not hasattr(cls, method_name):
                    unimplemented.append((iface.__name__, method_name))
                else:
                    # Check that the method was not left as an abstractmethod on the class
                    class_attr = getattr(cls, method_name, None)
                    if getattr(class_attr, "__isabstractmethod__", False):
                        unimplemented.append((iface.__name__, method_name))

            # Inject default methods if missing
            for attr_name, attr_value in iface.__dict__.items():
                if getattr(attr_value, "__is_default_method__", False):
                    if not hasattr(cls, attr_name):
                        setattr(cls, attr_name, attr_value)

        if unimplemented:
            missing_desc = ", ".join(f"'{iface}.{method}'" for iface, method in unimplemented)
            raise InterfaceImplementationError(
                f"Class '{cls.__name__}' fails to implement interface methods: {missing_desc}"
            )

        # Validate @Override methods on cls
        for attr_name, attr_value in cls.__dict__.items():
            if getattr(attr_value, "__haven_override__", False):
                # Verify that this method exists in at least one interface or superclass
                overridden = False
                for iface in interfaces:
                    if hasattr(iface, attr_name):
                        overridden = True
                        break
                if not overridden:
                    for base in cls.__mro__[1:]:
                        if base is not object and hasattr(base, attr_name):
                            overridden = True
                            break
                if not overridden:
                    from haven.annotations import OverrideError
                    raise OverrideError(
                        f"Method '{attr_name}' in class '{cls.__name__}' is annotated with @Override "
                        f"but does not override any superclass or interface method."
                    )

        return cls
    return decorator


# ==============================================================================
# 2. JAVA 17 SEALED CLASSES
# ==============================================================================

class SealedClass:
    """
    Java 17 Sealed Class Base:
    Only classes specified in permits=[...] are allowed to extend this class.
    Usage:
        class Shape(SealedClass, permits=['Circle', 'Square']):
            pass
    """
    __permitted_subclasses__: Set[str] = set()

    def __init_subclass__(cls, permits: Optional[List[Union[str, Type]]] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if permits is not None:
            cls.__permitted_subclasses__ = {p if isinstance(p, str) else p.__name__ for p in permits}
        else:
            # Check parent permits
            for base in cls.__bases__:
                if hasattr(base, "__permitted_subclasses__") and base.__permitted_subclasses__:
                    if cls.__name__ not in base.__permitted_subclasses__:
                        from haven.annotations import SealedHierarchyError
                        raise SealedHierarchyError(
                            f"Class '{cls.__name__}' is not in permitted list {sorted(list(base.__permitted_subclasses__))} "
                            f"of sealed base class '{base.__name__}'"
                        )


# ==============================================================================
# 3. RICH JAVA-STYLE ENUMS (HavenEnum)
# ==============================================================================

class HavenEnumMeta(type):
    """Metaclass enabling Java-style enum syntax with constructors and fields."""
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        instances = {}
        ordinal = 0

        # Scan for enum constant declarations
        for attr, value in list(namespace.items()):
            if attr.startswith("_"):
                continue
            if isinstance(value, tuple):
                # Constructor with arguments: STATUS = (code, label)
                instance = cls(*value)
                instance._name = attr
                instance._ordinal = ordinal
                instances[attr] = instance
                setattr(cls, attr, instance)
                ordinal += 1
            elif not callable(value) and not isinstance(value, (property, classmethod, staticmethod)):
                instance = cls(value)
                instance._name = attr
                instance._ordinal = ordinal
                instances[attr] = instance
                setattr(cls, attr, instance)
                ordinal += 1

        cls.__members__ = instances
        return cls

    def __iter__(cls):
        return iter(cls.__members__.values())

    def __getitem__(cls, name: str):
        return cls.__members__[name]

    def __len__(cls):
        return len(cls.__members__)


class HavenEnum(metaclass=HavenEnumMeta):
    """
    Java java.lang.Enum equivalence:
    Supports custom constructor fields, instance methods, ordinal numbers,
    and value lookups.
    Usage:
        class Priority(HavenEnum):
            LOW = (1, "Low Priority")
            HIGH = (10, "Critical Priority")

            def __init__(self, level: int, label: str):
                self.level = level
                self.label = label

            def is_urgent(self) -> bool:
                return self.level >= 8
    """
    _name: str = ""
    _ordinal: int = 0

    def name(self) -> str:
        return self._name

    def ordinal(self) -> int:
        return self._ordinal

    @classmethod
    def values(cls) -> List[Any]:
        return list(cls.__members__.values())

    @classmethod
    def value_of(cls, name: str) -> Any:
        if name in cls.__members__:
            return cls.__members__[name]
        raise ValueError(f"No enum constant {cls.__name__}.{name}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self._name}"


# ==============================================================================
# 4. JAVA RECORDS (Data Carriers)
# ==============================================================================

def Record(cls: Optional[Type] = None):
    """
    Java 16+ Record construct:
    Produces an immutable data carrier class with canonical constructor,
    component accessors, equals/hashCode, and toString representation.
    In Haven, seamlessly aliases to ODCS @Durable record.
    """
    from haven.annotations import Durable
    return Durable(cls)


# ==============================================================================
# 5. GENERICS & TYPE BOUND CONSTRAINTS
# ==============================================================================

class TypeBound:
    """Enforces Java-style bounded generics: <T extends BoundClass>."""
    def __init__(self, bound: Type):
        self.bound = bound

    def validate(self, candidate: Any) -> bool:
        if isinstance(candidate, type):
            return issubclass(candidate, self.bound)
        return isinstance(candidate, self.bound)


class GenericContainer:
    """Base class for type-safe generic containers with runtime validation."""
    __generic_bound__: Optional[Type] = None

    def __init_subclass__(cls, bound: Optional[Type] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if bound is not None:
            cls.__generic_bound__ = bound

    def check_bound(self, item: Any):
        if self.__generic_bound__ is not None:
            if not isinstance(item, self.__generic_bound__):
                raise TypeError(
                    f"Item {item!r} of type '{type(item).__name__}' violates generic bound "
                    f"<{self.__generic_bound__.__name__}>"
                )

