from .CanOverrideConfig import CanOverrideConfig
from ..migrations import Migration


class MigrateRollbackCommand(CanOverrideConfig):
    """
    Rolls back the last batch of migrations.

    migrate:rollback
        {--c|connection=default : The connection you want to run migrations on}
        {--s|show : Shows the output of SQL for migrations that would be running}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
        ).rollback(output=self.option("show"))
