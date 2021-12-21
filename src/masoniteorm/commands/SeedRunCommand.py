from inflection import camelize, underscore

from ..seeds import Seeder
from .Command import Command


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

        seeder = Seeder(dry=self.option("dry"), seed_path=self.option("directory"))

        if self.argument("table") == "None":
            seeder.run_database_seed()
            seeder_seeded = "Database Seeder"

        else:

            table = self.argument("table")
            seeder_file = (
                f"{underscore(table)}_table_seeder.{camelize(table)}TableSeeder"
            )
            seeder.run_specific_seed(seeder_file)
            seeder_seeded = f"{camelize(table)}TableSeeder"

        self.line(f"<info>{seeder_seeded} seeded!</info>")
