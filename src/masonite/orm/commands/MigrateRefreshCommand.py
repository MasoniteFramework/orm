from cleo import Command
from src.masonite.orm.migrations.Migration import Migration


class MigrateRefreshCommand(Command):
    """
    Run migrations.

    migrate:refresh
        {--c|connection=default : The connection you want to run migrations on}
    """

    def handle(self):
        migration = Migration(command_class=self)

        migration.refresh()
