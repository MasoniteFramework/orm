from ..migrations import Migration

from .Command import Command


class MigrateFreshCommand(Command):
    """
    Drops all tables and migrates them again.

    migrate:fresh
        {--c|connection=default : The connection you want to run migrations on}
        {--d|directory=databases/migrations : The location of the migration directory}
        {--f|ignore-fk=? : The connection you want to run migrations on}
        {--s|seed=? : Seed database after fresh. The seeder to be ran can be provided in argument}
        {--schema=? : Sets the schema to be migrated}
        {--D|seed-directory=databases/seeds : The location of the seed directory if seed option is used.}
    """

    def handle(self):
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
            schema=self.option("schema"),
        )

        migration.fresh(ignore_fk=self.option("ignore-fk"))

        self.line("")

        if self.option("seed") == "null":
            self.call(
                "seed:run",
                f"None --directory {self.option('seed-directory')} --connection {self.option('connection')}",
            )

        elif self.option("seed"):
            self.call(
                "seed:run",
                f"{self.option('seed')} --directory {self.option('seed-directory')} --connection {self.option('connection')}",
            )
