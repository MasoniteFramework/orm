from cleo import Command
from ..migrations import Migration


class MigrateRefreshCommand(Command):
    """
    Rolls back all migrations and migrates them again.

    migrate:refresh
        {--c|connection=default : The connection you want to run migrations on}
        {--d|directory=databases/migrations : The location of the migration directory}
        {--s|seed : Wheter seeding should be run after refresh migrations}
        {--seeder=None : Which seeder should be run}
    """

    def handle(self):
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
        )
        migration.refresh()

        if self.option("seed"):
            self.call("seed:run", self.option("seeder"))
