from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from packaging.version import Version

from byte.support import Yaml

if TYPE_CHECKING:
    from byte.foundation import Application


class BaseMigration(ABC):
    """Base class for config migrations."""

    @property
    @abstractmethod
    def target_version(self) -> str:
        """The version this migration upgrades to (e.g., '1.0.0')."""
        pass

    @abstractmethod
    def migrate(self, config: dict) -> dict:
        """Apply migration transformations to config."""
        pass


class Migrator:
    """Handles sequential config migrations."""

    def __init__(self, app: Application):
        self.app = app

    def _discover_migrations(self) -> list[BaseMigration]:
        """Discover and load migration modules in order."""
        migrations_dir = self.app.app_path("config/migrations")
        migration_files = sorted(migrations_dir.glob("migration_*.py"))

        migrations = []
        for file_path in migration_files:
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "Migration"):
                migrations.append(module.Migration())

        # Sort by target version
        migrations.sort(key=lambda m: Version(m.target_version))
        return migrations

    def _needs_migration(self, config_version: str, migration_version: str) -> bool:
        """Check if migration should be applied."""
        return Version(config_version) < Version(migration_version)

    def handle(self, config: dict) -> dict:
        """Apply all necessary migrations sequentially."""
        current_version = config.get("version", "0.0.0")
        migrations = self._discover_migrations()

        for migration in migrations:
            if self._needs_migration(current_version, migration.target_version):
                self.app["console"].print(f"Running migration to version {migration.target_version}")
                config = migration.migrate(config)
                current_version = config.get("version")

        # Write our changes back to the config file.
        config_path = self.app.config_path("config.yaml")
        Yaml.save(config_path, config)

        return config
