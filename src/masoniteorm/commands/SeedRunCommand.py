from cleo import Command
from ..seeds import Seeder
from inflection import camelize, underscore


class SeedRunCommand(Command):
    """
    Run seeds.

    seed:run
        {--c|connection=default : The connection you want to run migrations on}
        {--dry : If the seed should run in dry mode}
        {table=None : Name of the table to seed}
        {--d|directory=databases/seeds : The location of the seed directory}
    """

    def handle(self):
        if self.argument("table") == "None":
            return Seeder(
                dry=self.option("dry"), seed_path=self.option("directory")
            ).run_database_seed()

        file_name = f"{underscore(self.argument('table'))}_table_seeder.{camelize(self.argument('table'))}TableSeeder"

        return Seeder(
            dry=self.option("dry"), seed_path=self.option("directory")
        ).run_specific_seed(file_name)
