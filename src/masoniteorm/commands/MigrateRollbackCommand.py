from cleo import Command

from ..migrations import Migration


class MigrateRollbackCommand(Command):
    """
    Rolls back the last batch of migrations.

    migrate:rollback
        {--c|connection=default : The connection you want to run migrations on}
        {--s|show : Shows the output of SQL for migrations that would be running}
    """

    def handle(self):
        Migration(command_class=self, connection=self.option("connection")).rollback(
            output=self.option("show")
        )
