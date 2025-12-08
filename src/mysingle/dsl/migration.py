"""
DSL Version Migration - Tools for upgrading DSL code between versions

Provides migration strategies, compatibility layers, and version negotiation
for seamless DSL version upgrades across services.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from mysingle.core.logging import get_structured_logger
from mysingle.dsl.runtime_service import DSLVersion

logger = get_structured_logger(__name__)


class MigrationStrategy(Enum):
    """Migration strategies for version upgrades"""

    AUTO = "auto"  # Automatic migration with AST transformation
    MANUAL = "manual"  # Manual migration required
    COMPATIBLE = "compatible"  # No migration needed (backward compatible)
    DEPRECATED = "deprecated"  # Feature deprecated, warn user


@dataclass
class MigrationRule:
    """Rule for migrating DSL code between versions"""

    from_version: DSLVersion
    to_version: DSLVersion
    strategy: MigrationStrategy
    description: str
    transformer: Optional[Callable[[str], str]] = None  # Code transformation function
    breaking_changes: List[str] = field(default_factory=list)


@dataclass
class MigrationResult:
    """Result of DSL code migration"""

    success: bool
    migrated_code: Optional[str] = None
    original_version: Optional[DSLVersion] = None
    target_version: Optional[DSLVersion] = None
    changes_applied: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class DSLVersionRegistry:
    """
    Registry of DSL versions and migration rules

    Manages version compatibility matrix and migration paths
    """

    def __init__(self):
        self._migration_rules: Dict[tuple[str, str], MigrationRule] = {}
        self._supported_versions: List[DSLVersion] = []

        # Register default migration rules
        self._register_default_rules()

        logger.info("DSL version registry initialized")

    def _register_default_rules(self):
        """Register default migration rules"""

        # 1.0.0 -> 1.1.0: Type system added
        self.register_rule(
            MigrationRule(
                from_version=DSLVersion(1, 0, 0),
                to_version=DSLVersion(1, 1, 0),
                strategy=MigrationStrategy.COMPATIBLE,
                description="Added type inference, backward compatible",
                breaking_changes=[],
            )
        )

        # 1.1.0 -> 1.2.0: Standard library expansion
        self.register_rule(
            MigrationRule(
                from_version=DSLVersion(1, 1, 0),
                to_version=DSLVersion(1, 2, 0),
                strategy=MigrationStrategy.COMPATIBLE,
                description="Added new stdlib functions, backward compatible",
                breaking_changes=[],
            )
        )

        # 1.2.0 -> 1.3.0: Runtime service unification
        self.register_rule(
            MigrationRule(
                from_version=DSLVersion(1, 2, 0),
                to_version=DSLVersion(1, 3, 0),
                strategy=MigrationStrategy.COMPATIBLE,
                description="Unified runtime service, backward compatible",
                breaking_changes=[],
            )
        )

        # Example: 2.0.0 would have breaking changes
        # self.register_rule(MigrationRule(
        #     from_version=DSLVersion(1, 3, 0),
        #     to_version=DSLVersion(2, 0, 0),
        #     strategy=MigrationStrategy.AUTO,
        #     description="Major version upgrade with breaking changes",
        #     transformer=self._migrate_1_to_2,
        #     breaking_changes=[
        #         "RSI signature changed from RSI(data, period) to RSI(period)(data)",
        #         "Removed deprecated function: old_indicator()"
        #     ]
        # ))

        # Register supported versions
        self._supported_versions = [
            DSLVersion(1, 0, 0),
            DSLVersion(1, 1, 0),
            DSLVersion(1, 2, 0),
            DSLVersion(1, 3, 0),
        ]

    def register_rule(self, rule: MigrationRule):
        """Register a migration rule"""
        key = (str(rule.from_version), str(rule.to_version))
        self._migration_rules[key] = rule

        logger.info(
            "Migration rule registered",
            from_version=str(rule.from_version),
            to_version=str(rule.to_version),
            strategy=rule.strategy.value,
        )

    def get_rule(
        self, from_version: DSLVersion, to_version: DSLVersion
    ) -> Optional[MigrationRule]:
        """Get migration rule for version pair"""
        key = (str(from_version), str(to_version))
        return self._migration_rules.get(key)

    def is_version_supported(self, version: DSLVersion) -> bool:
        """Check if version is supported"""
        return version in self._supported_versions

    def get_migration_path(
        self, from_version: DSLVersion, to_version: DSLVersion
    ) -> List[MigrationRule]:
        """
        Find migration path from one version to another

        Returns list of migration rules to apply in sequence
        """
        if from_version == to_version:
            return []

        # Simple implementation: direct path only
        # TODO: Implement multi-hop path finding if needed
        rule = self.get_rule(from_version, to_version)
        if rule:
            return [rule]

        # Try to find intermediate versions
        path = []
        current = from_version

        for supported_version in sorted(self._supported_versions):
            if current < supported_version <= to_version:
                rule = self.get_rule(current, supported_version)
                if rule:
                    path.append(rule)
                    current = supported_version

        if current == to_version:
            return path

        logger.warning(
            "No migration path found",
            from_version=str(from_version),
            to_version=str(to_version),
        )
        return []


class DSLMigrationTool:
    """
    Tool for migrating DSL code between versions

    Usage:
        tool = DSLMigrationTool()
        result = await tool.migrate(
            code="RSI(close, 14)",
            from_version="1.0.0",
            to_version="2.0.0"
        )
    """

    def __init__(self, registry: Optional[DSLVersionRegistry] = None):
        """
        Initialize migration tool

        Args:
            registry: Version registry (creates default if None)
        """
        self.registry = registry or DSLVersionRegistry()

        logger.info("DSL migration tool initialized")

    async def migrate(
        self, code: str, from_version: str, to_version: str, auto_apply: bool = False
    ) -> MigrationResult:
        """
        Migrate DSL code from one version to another

        Args:
            code: DSL source code
            from_version: Current version string
            to_version: Target version string
            auto_apply: Automatically apply transformations

        Returns:
            MigrationResult with migrated code and metadata
        """
        from_ver = DSLVersion.from_string(from_version)
        to_ver = DSLVersion.from_string(to_version)

        logger.info(
            "Starting DSL migration",
            from_version=from_version,
            to_version=to_version,
            code_length=len(code),
            auto_apply=auto_apply,
        )

        # Check if versions are supported
        if not self.registry.is_version_supported(from_ver):
            return MigrationResult(
                success=False, errors=[f"Unsupported source version: {from_version}"]
            )

        if not self.registry.is_version_supported(to_ver):
            return MigrationResult(
                success=False, errors=[f"Unsupported target version: {to_version}"]
            )

        # Check if already compatible
        if from_ver.is_compatible(to_ver) and from_ver.major == to_ver.major:
            return MigrationResult(
                success=True,
                migrated_code=code,
                original_version=from_ver,
                target_version=to_ver,
                warnings=["Versions are compatible, no migration needed"],
            )

        # Get migration path
        path = self.registry.get_migration_path(from_ver, to_ver)

        if not path:
            return MigrationResult(
                success=False,
                original_version=from_ver,
                target_version=to_ver,
                errors=[f"No migration path from {from_version} to {to_version}"],
            )

        # Apply migrations in sequence
        current_code = code
        changes_applied = []
        warnings = []

        for rule in path:
            logger.info(
                "Applying migration rule",
                from_version=str(rule.from_version),
                to_version=str(rule.to_version),
                strategy=rule.strategy.value,
            )

            if rule.strategy == MigrationStrategy.COMPATIBLE:
                # No transformation needed
                changes_applied.append(
                    f"Compatible upgrade: {rule.from_version} -> {rule.to_version}"
                )
                continue

            elif rule.strategy == MigrationStrategy.AUTO and rule.transformer:
                # Apply automatic transformation
                if auto_apply:
                    try:
                        current_code = rule.transformer(current_code)
                        changes_applied.append(
                            f"Auto-migrated: {rule.from_version} -> {rule.to_version}"
                        )
                    except Exception as e:
                        logger.error("Migration transformation failed", error=str(e))
                        return MigrationResult(
                            success=False,
                            original_version=from_ver,
                            target_version=to_ver,
                            errors=[f"Transformation failed: {str(e)}"],
                        )
                else:
                    warnings.append(
                        f"Manual review needed for {rule.from_version} -> {rule.to_version}"
                    )

            elif rule.strategy == MigrationStrategy.MANUAL:
                # Manual migration required
                warnings.append(f"Manual migration required: {rule.description}")
                for change in rule.breaking_changes:
                    warnings.append(f"  - {change}")

            elif rule.strategy == MigrationStrategy.DEPRECATED:
                # Feature deprecated
                warnings.append(f"Deprecated feature: {rule.description}")

        logger.info(
            "DSL migration complete",
            from_version=from_version,
            to_version=to_version,
            changes_count=len(changes_applied),
            warnings_count=len(warnings),
        )

        return MigrationResult(
            success=True,
            migrated_code=current_code,
            original_version=from_ver,
            target_version=to_ver,
            changes_applied=changes_applied,
            warnings=warnings,
        )

    async def check_compatibility(self, code: str, version: str) -> Dict[str, Any]:
        """
        Check if DSL code is compatible with a specific version

        Returns dict with compatibility info
        """
        # This would involve parsing and checking against version-specific rules
        # For now, basic implementation
        return {
            "version": version,
            "compatible": True,
            "warnings": [],
            "deprecated_features": [],
        }


# Global registry instance
_global_registry = DSLVersionRegistry()


def get_version_registry() -> DSLVersionRegistry:
    """Get global version registry"""
    return _global_registry
