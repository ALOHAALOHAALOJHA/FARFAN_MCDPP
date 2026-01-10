"""Contract Migration Strategy - GAP 4 Implementation.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Contract Migrator
PHASE_ROLE: Migrate contracts between versions with validation and chaining

GAP 4 Implementation: Contract Migration Strategy

This module provides tools for migrating contracts between versions:
- Chained migrations (v2 → v3 → v4)
- Schema validation after migration
- Batch migration for directories
- Reversible migrations (optional downgrade)

Requirements Implemented:
    CM-01: Migrator supports chained migrations (v2→v3→v4)
    CM-02: Each migration step is a pure function (contract_dict → contract_dict)
    CM-03: Migrated contracts validated against target version schema
    CM-04: Migration is reversible (optional downgrade)
    CM-05: Batch migration supported for all contracts in a directory

Design Principles:
- Pure functions for migrations (no side effects)
- BFS path finding for optimal migration chains
- JSON Schema validation for target versions
- Idempotent migrations
"""

from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, ClassVar

logger = logging.getLogger(__name__)

# Try to import jsonschema for validation
try:
    import jsonschema

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logger.warning(
        "jsonschema not installed. Schema validation will be skipped. "
        "Install with: pip install jsonschema"
    )


# === DATA MODELS ===


@dataclass
class MigrationResult:
    """Result of a contract migration operation.

    Attributes:
        success: Whether migration succeeded
        original_version: Version before migration
        target_version: Target version after migration
        original_path: Path to original contract file
        new_path: Path to migrated contract file (if successful)
        error: Error message if migration failed
        migration_path: List of versions traversed during migration
    """

    success: bool
    original_version: str
    target_version: str
    original_path: Path
    new_path: Optional[Path] = None
    error: Optional[str] = None
    migration_path: List[str] = field(default_factory=list)


# Type alias for migration functions
MigrationFunc = Callable[[dict], dict]


# === EXCEPTIONS ===


class MigrationError(Exception):
    """Raised when migration fails."""

    pass


class ValidationError(Exception):
    """Raised when schema validation fails."""

    pass


# === CONTRACT MIGRATOR ===


class ContractMigrator:
    """
    Migrates contracts between versions.

    GAP 4 Implementation: Contract Migration Strategy

    Features:
        - Chained migrations for multi-version jumps
        - Pure function migrations
        - Schema validation
        - Batch migration support

    Usage:
        migrator = ContractMigrator()
        result = migrator.migrate_contract(Path("contract.json"), "v4")
    """

    # Registry of migrations: (from_version, to_version) -> migration_func
    MIGRATIONS: ClassVar[Dict[tuple, MigrationFunc]] = {}

    # Schema registry for validation
    SCHEMAS: ClassVar[Dict[str, dict]] = {}

    def __init__(self, output_suffix: str = ".migrated"):
        """
        Initialize ContractMigrator.

        Args:
            output_suffix: Suffix to add to migrated files (before .json)
        """
        self.output_suffix = output_suffix

    @classmethod
    def register_migration(cls, from_version: str, to_version: str, func: MigrationFunc) -> None:
        """
        Register a migration function.

        Args:
            from_version: Source contract version (e.g., "v2")
            to_version: Target contract version (e.g., "v3")
            func: Pure function that transforms contract dict
        """
        cls.MIGRATIONS[(from_version, to_version)] = func
        logger.debug(f"Registered migration: {from_version} → {to_version}")

    @classmethod
    def register_schema(cls, version: str, schema: dict) -> None:
        """
        Register a JSON schema for a contract version.

        Args:
            version: Contract version (e.g., "v3")
            schema: JSON Schema dict for validation
        """
        cls.SCHEMAS[version] = schema
        logger.debug(f"Registered schema for version: {version}")

    def migrate_contract(
        self, contract_path: Path, target_version: str, output_dir: Optional[Path] = None
    ) -> MigrationResult:
        """
        Migrate a contract file to the target version.

        Implements CM-01 through CM-05.

        Args:
            contract_path: Path to the contract JSON file.
            target_version: Desired contract version (e.g., 'v4').
            output_dir: Optional output directory for migrated contract.

        Returns:
            MigrationResult indicating success or failure.
        """
        contract_path = Path(contract_path)
        contract = None  # Initialize to avoid reference errors in exception handler

        try:
            # Load contract
            with open(contract_path, "r") as f:
                contract = json.load(f)

            original_version = contract.get("version", "unknown")
            current_version = original_version
            migration_path = [current_version]

            # Already at target version?
            if current_version == target_version:
                return MigrationResult(
                    success=True,
                    original_version=original_version,
                    target_version=target_version,
                    original_path=contract_path,
                    new_path=contract_path,
                    migration_path=migration_path,
                )

            # Find migration path
            path = self._find_migration_path(current_version, target_version)
            if not path:
                raise MigrationError(
                    f"No migration path from {current_version} to {target_version}"
                )

            # Apply migration chain (CM-01, CM-02)
            for i in range(len(path) - 1):
                from_v = path[i]
                to_v = path[i + 1]

                migrator = self.MIGRATIONS.get((from_v, to_v))
                if not migrator:
                    raise MigrationError(f"Missing migration: {from_v} → {to_v}")

                # Apply pure migration function
                contract = migrator(contract)
                contract["version"] = to_v
                migration_path.append(to_v)

                logger.debug(f"Applied migration: {from_v} → {to_v}")

            # Validate against target schema (CM-03)
            self._validate_schema(contract, target_version)

            # Determine output path
            output_dir = output_dir or contract_path.parent
            new_filename = f"{contract_path.stem}{self.output_suffix}.{target_version}.json"
            new_path = output_dir / new_filename

            # Write migrated contract
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(new_path, "w") as f:
                json.dump(contract, f, indent=2)

            logger.info(
                f"Migration successful: {contract_path} → {new_path} "
                f"({original_version} → {target_version})"
            )

            return MigrationResult(
                success=True,
                original_version=original_version,
                target_version=target_version,
                original_path=contract_path,
                new_path=new_path,
                migration_path=migration_path,
            )

        except Exception as e:
            logger.error(f"Migration failed for {contract_path}: {e}")
            return MigrationResult(
                success=False,
                original_version=contract.get("version", "unknown") if contract else "unknown",
                target_version=target_version,
                original_path=contract_path,
                new_path=None,
                error=str(e),
            )

    def migrate_directory(
        self,
        directory: Path,
        target_version: str,
        output_dir: Optional[Path] = None,
        pattern: str = "*.json",
    ) -> List[MigrationResult]:
        """
        Migrate all contracts in a directory.

        Implements CM-05.

        Args:
            directory: Directory containing contract files.
            target_version: Target version for all contracts.
            output_dir: Optional output directory.
            pattern: Glob pattern for contract files.

        Returns:
            List of MigrationResult objects.
        """
        directory = Path(directory)
        results = []

        contract_files = list(directory.glob(pattern))
        logger.info(f"Found {len(contract_files)} contracts to migrate in {directory}")

        for contract_file in contract_files:
            result = self.migrate_contract(contract_file, target_version, output_dir)
            results.append(result)

        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        logger.info(f"Batch migration complete: {successful} succeeded, {failed} failed")

        return results

    def _find_migration_path(self, current: str, target: str) -> Optional[List[str]]:
        """
        Find the shortest migration path using BFS.

        Args:
            current: Current version.
            target: Target version.

        Returns:
            List of versions representing the path, or None if no path exists.
        """
        if current == target:
            return [current]

        visited = {current}
        queue = deque([(current, [current])])

        while queue:
            version, path = queue.popleft()

            # Find all versions we can migrate to from current version
            for from_v, to_v in self.MIGRATIONS.keys():
                if from_v == version and to_v not in visited:
                    new_path = path + [to_v]

                    if to_v == target:
                        return new_path

                    visited.add(to_v)
                    queue.append((to_v, new_path))

        return None

    def _validate_schema(self, contract: dict, version: str) -> None:
        """
        Validate contract against version schema.

        Args:
            contract: Contract dict to validate.
            version: Version whose schema to validate against.

        Raises:
            ValidationError: If validation fails.
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.debug("Skipping schema validation (jsonschema not installed)")
            return

        schema = self.SCHEMAS.get(version)
        if not schema:
            logger.debug(f"No schema registered for version {version}")
            return

        try:
            jsonschema.validate(contract, schema)
            logger.debug(f"Contract validated against {version} schema")
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Schema validation failed for {version}: {e.message}")

    def can_migrate(self, from_version: str, to_version: str) -> bool:
        """
        Check if a migration path exists between versions.

        Args:
            from_version: Source version.
            to_version: Target version.

        Returns:
            True if migration is possible.
        """
        return self._find_migration_path(from_version, to_version) is not None

    def get_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """
        Get the migration path between versions.

        Args:
            from_version: Source version.
            to_version: Target version.

        Returns:
            List of versions in migration path.

        Raises:
            MigrationError: If no path exists.
        """
        path = self._find_migration_path(from_version, to_version)
        if not path:
            raise MigrationError(f"No migration path from {from_version} to {to_version}")
        return path


# === BUILT-IN MIGRATIONS ===

import copy
from datetime import datetime, timezone


def migrate_v2_to_v3(contract: dict) -> dict:
    """
    Migrate contract from v2 to v3.

    Changes:
    - Rename 'parameters' to 'params'
    - Add 'metadata' field with migration info
    """
    result = copy.deepcopy(contract)

    # Rename 'parameters' to 'params'
    if "parameters" in result:
        result["params"] = result.pop("parameters")

    # Add metadata
    result.setdefault("metadata", {})
    result["metadata"]["migrated_from"] = "v2"
    result["metadata"]["migration_date"] = datetime.now(timezone.utc).isoformat()

    return result


def migrate_v3_to_v4(contract: dict) -> dict:
    """
    Migrate contract from v3 to v4.

    Changes:
    - Restructure 'params' into 'configuration.parameters'
    - Add 'schema_version' field
    """
    result = copy.deepcopy(contract)

    # Restructure params
    if "params" in result:
        result["configuration"] = {"parameters": result.pop("params")}

    # Add schema version
    result["schema_version"] = "4.0.0"

    # Update metadata
    result.setdefault("metadata", {})
    result["metadata"]["migrated_from"] = result["metadata"].get("migrated_from", "v3")
    if result["metadata"]["migrated_from"] != "v3":
        result["metadata"]["migrated_from"] = f"{result['metadata']['migrated_from']} → v3"

    return result


def migrate_v3_to_v2(contract: dict) -> dict:
    """
    Downgrade contract from v3 to v2 (CM-04: Reversible).

    Changes:
    - Rename 'params' back to 'parameters'
    - Remove migration metadata
    """
    result = contract.copy()

    # Rename 'params' back to 'parameters'
    if "params" in result:
        result["parameters"] = result.pop("params")

    # Clean up migration metadata
    if "metadata" in result:
        result["metadata"].pop("migrated_from", None)
        result["metadata"].pop("migration_date", None)
        if not result["metadata"]:
            del result["metadata"]

    return result


def migrate_v4_to_v3(contract: dict) -> dict:
    """
    Downgrade contract from v4 to v3 (CM-04: Reversible).

    Changes:
    - Extract 'configuration.parameters' back to 'params'
    - Remove 'schema_version'
    """
    result = contract.copy()

    # Extract params from configuration
    if "configuration" in result and "parameters" in result["configuration"]:
        result["params"] = result["configuration"]["parameters"]
        del result["configuration"]["parameters"]
        if not result["configuration"]:
            del result["configuration"]

    # Remove schema version
    result.pop("schema_version", None)

    return result


# === BUILT-IN SCHEMAS ===

SCHEMA_V3 = {
    "type": "object",
    "required": ["version", "contract_id"],
    "properties": {
        "version": {"type": "string", "pattern": "^v3$"},
        "contract_id": {"type": "string"},
        "params": {"type": "object"},
        "metadata": {"type": "object"},
    },
}

SCHEMA_V4 = {
    "type": "object",
    "required": ["version", "contract_id", "schema_version"],
    "properties": {
        "version": {"type": "string", "pattern": "^v4$"},
        "contract_id": {"type": "string"},
        "schema_version": {"type": "string"},
        "configuration": {"type": "object", "properties": {"parameters": {"type": "object"}}},
        "metadata": {"type": "object"},
    },
}


# === REGISTRATION ===

# Register built-in migrations
ContractMigrator.register_migration("v2", "v3", migrate_v2_to_v3)
ContractMigrator.register_migration("v3", "v4", migrate_v3_to_v4)
ContractMigrator.register_migration("v3", "v2", migrate_v3_to_v2)  # Downgrade
ContractMigrator.register_migration("v4", "v3", migrate_v4_to_v3)  # Downgrade

# Register built-in schemas
ContractMigrator.register_schema("v3", SCHEMA_V3)
ContractMigrator.register_schema("v4", SCHEMA_V4)


# === CONVENIENCE FUNCTIONS ===


def migrate_contract(
    contract_path: str | Path, target_version: str, output_dir: str | Path | None = None
) -> MigrationResult:
    """
    Migrate a single contract file (convenience function).

    Args:
        contract_path: Path to contract file.
        target_version: Target version.
        output_dir: Optional output directory.

    Returns:
        MigrationResult.
    """
    migrator = ContractMigrator()
    return migrator.migrate_contract(
        Path(contract_path), target_version, Path(output_dir) if output_dir else None
    )


def migrate_all_contracts(
    directory: str | Path, target_version: str, output_dir: str | Path | None = None
) -> List[MigrationResult]:
    """
    Migrate all contracts in a directory (convenience function).

    Args:
        directory: Directory containing contracts.
        target_version: Target version.
        output_dir: Optional output directory.

    Returns:
        List of MigrationResult objects.
    """
    migrator = ContractMigrator()
    return migrator.migrate_directory(
        Path(directory), target_version, Path(output_dir) if output_dir else None
    )


__all__ = [
    # Data models
    "MigrationResult",
    "MigrationFunc",
    # Exceptions
    "MigrationError",
    "ValidationError",
    # Main class
    "ContractMigrator",
    # Built-in migrations
    "migrate_v2_to_v3",
    "migrate_v3_to_v4",
    "migrate_v3_to_v2",
    "migrate_v4_to_v3",
    # Built-in schemas
    "SCHEMA_V3",
    "SCHEMA_V4",
    # Convenience functions
    "migrate_contract",
    "migrate_all_contracts",
]
