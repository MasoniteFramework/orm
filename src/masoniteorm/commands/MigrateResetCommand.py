from ..migrations import Migration
from .Command import Command


class MigrateResetCommand(Command):
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
            config_path=self.option("config"),
        )
        migration.reset()
