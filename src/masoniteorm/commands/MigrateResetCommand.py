from .CanOverrideConfig import CanOverrideConfig
from ..migrations import Migration


class MigrateResetCommand(CanOverrideConfig):
    """
    Rolls back all migrations.

    migrate:reset
        {--c|connection=default : The connection you want to run migrations on}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("option"),
        )
        migration.reset()
