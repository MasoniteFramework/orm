import datetime
import os
import pathlib

from cleo import Command
from inflection import camelize

from ..migrations import Migration
from inflection import underscore


class MakeSeedCommand(Command):
    """
    Creates a new seed file.

    seed
        {name : The name of the seed}
    """

    def handle(self):
        # get the contents of a stub file
        # replace the placeholders of a stub file
        # output the content to a file location
        name = self.argument("name") + "TableSeeder"
        seed_directory = "databases/seeds"

        file_name = underscore(name)
        stub_file = "create_seed"

        with open(
            os.path.join(
                pathlib.Path(__file__).parent.absolute(), f"stubs/{stub_file}.stub"
            )
        ) as fp:
            output = fp.read()
            output = output.replace("__SEEDER_NAME__", camelize(name))

        file_name = f"{underscore(name)}.py"
        full_path = os.path.join(os.getcwd(), seed_directory, file_name)
        if os.path.exists(full_path):
            return self.line(f"<error>{full_path} already exists.</error>")

        with open(full_path, "w") as fp:
            fp.write(output)

        self.info(f"Seed file created: {file_name}")
