import os
import pathlib

from inflection import camelize, underscore

from .Command import Command


class MakeSeedCommand(Command):
    """
    Creates a new seed file.

    seed
        {name : The name of the seed}
        {--d|directory=databases/seeds : The location of the seed directory}
    """

    def handle(self):
        # get the contents of a stub file
        # replace the placeholders of a stub file
        # output the content to a file location
        name = self.argument("name") + "TableSeeder"
        seed_directory = self.option("directory")

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
        full_path = pathlib.Path(os.path.join(os.getcwd(), seed_directory, file_name))

        path_normalized = pathlib.Path(seed_directory) / pathlib.Path(file_name)

        if os.path.exists(full_path):
            return self.line(f"<error>{path_normalized} already exists.</error>")

        with open(full_path, "w") as fp:
            fp.write(output)

        self.info(f"Seed file created: {path_normalized}")
