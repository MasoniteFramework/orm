from ..migrations import Migration

from .Command import Command


class MigrateRefreshCommand(Command):
    """
    Rolls back all migrations and migrates them again.

    migrate:refresh
        {--c|connection=default : The connection you want to run migrations on}
        {--d|directory=databases/migrations : The location of the migration directory}
        {--s|seed=? : Seed database after refresh. The seeder to be ran can be provided in argument}
        {--D|seed-directory=databases/seeds : The location of the seed directory if seed option is used.}
    """

    def handle(self):

        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
        )

        migration.refresh()

        self.line("")

        if self.option("seed") == "null":
            self.call("seed:run", f"None --directory {self.option('seed-directory')}")
        elif self.option("seed"):
            self.call(
                "seed:run",
                f"{self.option('seed')} --directory {self.option('seed-directory')}",
            )
