from cleo import Command
from src.masonite.orm.migrations.Migration import Migration


class MigrateCommand(Command):
    """
    Run migrations.

    migrate
        {--c|connection=default : The connection you want to run migrations on}
    """

    def handle(self):
        migration = Migration(command_class=self)
        if not migration.get_unran_migrations():
            self.info("Nothing to migrate")

        migration.migrate()
