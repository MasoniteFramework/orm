from cleo import Command
from ..migrations import Migration


class MigrateResetCommand(Command):
    """
    Rolls back all migrations.

    migrate:reset
        {--c|connection=default : The connection you want to run migrations on}
    """

    def handle(self):
        migration = Migration(command_class=self, connection=self.option("connection"))
        migration.reset()
