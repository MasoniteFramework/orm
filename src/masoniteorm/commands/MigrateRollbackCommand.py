from .CanOverrideConfig import CanOverrideConfig
from ..migrations import Migration


class MigrateRollbackCommand(CanOverrideConfig):
    """
    Rolls back the last batch of migrations.

    migrate:rollback
        {--m|migration=all : Migration's name to be rollback}
        {--c|connection=default : The connection you want to run migrations on}
        {--s|show : Shows the output of SQL for migrations that would be running}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
        ).rollback(
            migration=self.option("migration"),
            config_path=self.option("config"),
            output=self.option("show"),
        )
