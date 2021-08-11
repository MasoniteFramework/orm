import os
import pathlib

from cleo import Command
from inflection import camelize, underscore, tableize


class MakeModelCommand(Command):
    """
    Creates a new model file.

    model
        {name : The name of the model}
        {--m|migration : Optionally create a migration file}
        {--c|create : If the migration file should create a table}
        {--t|table : If the migration file should modify an existing table}
        {--d|directory=app : The location of the model directory}
    """

    def handle(self):
        name = self.argument("name")

        model_directory = self.option("directory")

        with open(
            os.path.join(pathlib.Path(__file__).parent.absolute(), f"stubs/model.stub")
        ) as fp:
            output = fp.read()
            output = output.replace("__CLASS__", camelize(name))

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
            if self.option("create"):
                self.call(
                    "migration",
                    f"create_{tableize(name)}_table --create {tableize(name)}",
                )
            else:
                self.call(
                    "migration",
                    f"update_{tableize(name)}_table --table {tableize(name)}",
                )
