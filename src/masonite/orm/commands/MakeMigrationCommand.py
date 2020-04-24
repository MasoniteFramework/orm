import datetime
import os
import pathlib

from cleo import Command
from inflection import camelize

from src.masonite.orm.migrations.Migration import Migration


class MakeMigrationCommand(Command):
    """
    Run migrations.

    migration
        {name : Make a new migration}
        {--c|create=None : The table to create}
        {--t|table=None : The table to alter}
    """

    def handle(self):
        # get the contents of a stub file
        # replace the placeholders of a stub file
        # output the content to a file location
        name = self.argument("name")
        now = datetime.datetime.today()

        if self.option("create") != "None":
            table = self.option("create")
            action = "create"
        else:
            table = self.option("table")
            action = "alter"

        if table == "None":
            raise ValueError(
                "You must supply a table name with either the --create or --table options"
            )

        migration_directory = "databases/migrations"

        with open(
            os.path.join(
                pathlib.Path(__file__).parent.absolute(), "stubs/migration_file.stub"
            )
        ) as fp:
            output = fp.read()
            output = output.replace("__MIGRATION_NAME__", camelize(name))
            output = output.replace("__TABLE_NAME__", table)
            if action == "create":
                output = output.replace(
                    "__PASS_OR_DROP__", 'self.schema.drop("__TABLE_NAME__")'
                )
                output = output.replace("__action__", "create")
            else:
                output = output.replace("__PASS_OR_DROP__", "pass")
                output = output.replace("__action__", "table")

        date_file = ""
        file_name = f"{now.strftime('%Y_%m_%d')}_{now.microsecond}_{name}.py"

        with open(os.path.join(os.getcwd(), migration_directory, file_name), "w") as fp:
            fp.write(output)

        self.info(f"Migration file created: {file_name}")
