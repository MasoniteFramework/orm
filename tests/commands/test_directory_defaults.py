import os
import unittest

from src.masoniteorm.commands import (
    MakeMigrationCommand,
    MakeModelCommand,
    MakeSeedCommand,
    MigrateCommand,
    SeedRunCommand,
)


class TestDirectoryDefaults(unittest.TestCase):
    def setUp(self):
        self.original_db_config_path = os.getenv("DB_CONFIG_PATH")
        os.environ["DB_CONFIG_PATH"] = "tests/integrations/config/folder_defaults"

    def tearDown(self):
        if self.original_db_config_path is None:
            os.environ.pop("DB_CONFIG_PATH", None)
        else:
            os.environ["DB_CONFIG_PATH"] = self.original_db_config_path

    def test_make_model_uses_configured_defaults(self):
        command = MakeModelCommand()

        self.assertEqual(
            command.option_or_config(
                "directory", "app", "MODELS_DIRECTORY", "models_directory"
            ),
            "custom-app",
        )
        self.assertEqual(
            command.option_or_config(
                "migrations-directory",
                "databases/migrations",
                "MIGRATIONS_DIRECTORY",
                "migrations_directory",
            ),
            "custom-databases/migrations",
        )
        self.assertEqual(
            command.option_or_config(
                "seeders-directory",
                "databases/seeds",
                "SEEDERS_DIRECTORY",
                "seeders_directory",
            ),
            "custom-databases/seeds",
        )

    def test_migration_and_seed_commands_use_configured_defaults(self):
        self.assertEqual(
            MigrateCommand().option_or_config(
                "directory",
                "databases/migrations",
                "MIGRATIONS_DIRECTORY",
                "migrations_directory",
            ),
            "custom-databases/migrations",
        )
        self.assertEqual(
            MakeMigrationCommand().option_or_config(
                "directory",
                "databases/migrations",
                "MIGRATIONS_DIRECTORY",
                "migrations_directory",
            ),
            "custom-databases/migrations",
        )
        self.assertEqual(
            MakeSeedCommand().option_or_config(
                "directory", "databases/seeds", "SEEDS_DIRECTORY", "seed_directory"
            ),
            "custom-databases/seeds",
        )
        self.assertEqual(
            SeedRunCommand().option_or_config(
                "directory", "databases/seeds", "SEEDS_DIRECTORY", "seed_directory"
            ),
            "custom-databases/seeds",
        )
