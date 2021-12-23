from ..migrations import Migration
from .Command import Command


class MigrateRollbackCommand(Command):
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
            config_path=self.option("config"),
        ).rollback(migration=self.option("migration"), output=self.option("show"))
