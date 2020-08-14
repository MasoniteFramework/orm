from cleo import Command
from ..migrations import Migration


class MigrateCommand(Command):
    """
    Run migrations.

    migrate
        {--c|connection=default : The connection you want to run migrations on}
    """

    def handle(self):
        migration = Migration(command_class=self)
        migration.create_table_if_not_exists()
        if not migration.get_unran_migrations():
            self.info("Nothing to migrate")

        migration.migrate()
