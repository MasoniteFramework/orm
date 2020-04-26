from cleo import Command

from ..migrations import Migration


class MigrateRollbackCommand(Command):
    """
    Rolls back the last batch of migrations.

    migrate:rollback
        {--c|connection=default : The connection you want to run migrations on}
    """

    def handle(self):
        Migration(command_class=self).rollback()
