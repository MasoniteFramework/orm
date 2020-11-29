from cleo import Command
from ..migrations import Migration
from ..seeds import Seeder
from inflection import camelize


class SeedRunCommand(Command):
    """
    Run seeds.

    seed:run
        {--c|connection=default : The connection you want to run migrations on}
        {--d|dry : If the seed should run in dry mode}
        {table=None : Name of the table to seed}
    """

    def handle(self):
        if self.argument("table") == "None":
            return Seeder(dry=self.option("dry")).run_database_seed()

        file_name = f"{self.argument('table')}_table_seeder.{camelize(self.argument('table'))}TableSeeder"

        return Seeder(dry=self.option("dry")).run_specific_seed(file_name)
