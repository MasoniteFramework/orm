from cleo import Command

from src.masonite.orm.migrations.Migration import Migration


class MigrateRollbackCommand(Command):
    """
    Run migrations.

    migrate:rollback
        {--c|connection=default : The connection you want to run migrations on}
    """

    def handle(self):
        Migration(command_class=self).rollback()
