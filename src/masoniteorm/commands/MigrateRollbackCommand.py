from ..migrations import Migration
from .Command import Command


class MigrateRollbackCommand(Command):
    """
    Rolls back the last batch of migrations.

    migrate:rollback
        {--m|migration=all : Migration's name to be rollback}
        {--c|connection=default : The connection you want to run migrations on}
        {--s|show : Shows the output of SQL for migrations that would be running}
        {--schema=? : Sets the schema to be migrated}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
            schema=self.option("schema"),
        ).rollback(migration=self.option("migration"), output=self.option("show"))
