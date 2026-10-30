"""
Open Digital Continuity Standard (ODCS) - Schema Evolution & Migration Engine.
Standard Specification by Anirudha Puthraya.
"""

from typing import Dict, Any, Callable, Optional, List
from .core import DurableRecord


class SchemaMigrationError(Exception):
    """Raised when a schema migration fails to preserve digital continuity."""
    pass


class ContinuitySchema:
    """
    ODCS Schema Definition & Lifecycle Manager.
    Guarantees cross-generational digital continuity by registering schema migrations
    and verifying deterministic compatibility between versions.
    """
    def __init__(self, name: str, version: str, fields: Dict[str, type], author: str = "Anirudha Puthraya") -> None:
        self.name: str = name
        self.version: str = version
        self.fields: Dict[str, type] = fields
        self.author: str = author
        self._migrations: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register_migration(self, target_version: str, migrator: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Register a forward migration function to a newer schema version."""
        self._migrations[target_version] = migrator

    def migrate(self, data: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """Apply migration pipeline to transform legacy record data to target_version."""
        if self.version == target_version:
            return dict(data)
        if target_version not in self._migrations:
            raise SchemaMigrationError(f"No ODCS migration path registered from {self.version} to {target_version}.")

        transformed = self._migrations[target_version](data)
        return transformed

    def validate(self, record_data: Dict[str, Any]) -> bool:
        """Verify that record_data conforms to the schema's defined field types."""
        for field_name, expected_type in self.fields.items():
            if field_name not in record_data:
                return False
            val = record_data[field_name]
            if not isinstance(val, expected_type):
                return False
        return True
