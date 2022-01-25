import os
import pathlib

from inflection import camelize, tableize, underscore

from .Command import Command


class MakeModelCommand(Command):
    """
    Creates a new model file.

    model
        {name : The name of the model}
        {--m|migration : Optionally create a migration file}
        {--s|seeder : Optionally create a seeder file}
        {--c|create : If the migration file should create a table}
        {--t|table : If the migration file should modify an existing table}
        {--p|pep : Makes the file into pep 8 standards}
        {--d|directory=app : The location of the model directory}
        {--D|migrations-directory=databases/migrations : The location of the migration directory}
        {--S|seeders-directory=databases/seeds : The location of the seeders directory}
    """

    def handle(self):
        name = self.argument("name")

        model_directory = self.option("directory")

        with open(
            os.path.join(pathlib.Path(__file__).parent.absolute(), f"stubs/model.stub")
        ) as fp:
            output = fp.read()
            output = output.replace("__CLASS__", camelize(name))

        if self.option("pep"):
            file_name = f"{underscore(name)}.py"
        else:
            file_name = f"{camelize(name)}.py"

        full_directory_path = os.path.join(os.getcwd(), model_directory)

        if os.path.exists(os.path.join(full_directory_path, file_name)):
            self.line(
                f'<error>Model "{name}" Already Exists ({full_directory_path}/{file_name})</error>'
            )
            return

        os.makedirs(os.path.dirname(os.path.join(full_directory_path)), exist_ok=True)

        with open(os.path.join(os.getcwd(), model_directory, file_name), "w+") as fp:
            fp.write(output)

        self.info(f"Model created: {os.path.join(model_directory, file_name)}")
        if self.option("migration"):
            migrations_directory = self.option("migrations-directory")
            if self.option("table"):
                self.call(
                    "migration",
                    f"update_{tableize(name)}_table --table {tableize(name)} --directory {migrations_directory}",
                )
            else:
                self.call(
                    "migration",
                    f"create_{tableize(name)}_table --create {tableize(name)} --directory {migrations_directory}",
                )

        if self.option("seeder"):
            directory = self.option("seeders-directory")
            self.call("seed", f"{self.argument('name')} --directory {directory}")
