import os
import pathlib

from inflection import camelize, underscore

from .Command import Command


class MakeObserverCommand(Command):
    """
    Creates a new observer file.

    observer
        {name : The name of the observer}
        {--m|model=None : The name of the model}
        {--d|directory=app/observers : The location of the observers directory}
    """

    def handle(self):
        name = self.argument("name")
        model = self.option("model")
        if model == "None":
            model = name

        observer_directory = self.option("directory")

        with open(
            os.path.join(
                pathlib.Path(__file__).parent.absolute(), f"stubs/observer.stub"
            )
        ) as fp:
            output = fp.read()
            output = output.replace("__CLASS__", camelize(name))
            output = output.replace("__MODEL_VARIABLE__", underscore(model))
            output = output.replace("__MODEL__", camelize(model))

        file_name = f"{camelize(name)}Observer.py"

        full_directory_path = os.path.join(os.getcwd(), observer_directory)

        if os.path.exists(os.path.join(full_directory_path, file_name)):
            self.line(
                f'<error>Observer "{name}" Already Exists ({full_directory_path}/{file_name})</error>'
            )
            return

        os.makedirs(os.path.join(full_directory_path), exist_ok=True)

        with open(os.path.join(os.getcwd(), observer_directory, file_name), "w+") as fp:
            fp.write(output)

        self.info(f"Observer created: {file_name}")
