import datetime
import os
import pathlib

from cleo import Command
from inflection import camelize

from ..migrations import Migration


class MakeMigrationCommand(Command):
    """
    Creates a new migration file.

    migration
        {name : The name of the migration}
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
            stub_file = "create_migration"
        else:
            table = self.option("table")
            stub_file = "table_migration"

        if table == "None":
            raise ValueError(
                "You must supply a table name with either the --create or --table options"
            )

        migration_directory = "databases/migrations"

        with open(
            os.path.join(
                pathlib.Path(__file__).parent.absolute(), f"stubs/{stub_file}.stub"
            )
        ) as fp:
            output = fp.read()
            output = output.replace("__MIGRATION_NAME__", camelize(name))
            output = output.replace("__TABLE_NAME__", table)

        file_name = f"{now.strftime('%Y_%m_%d')}_{now.microsecond}_{name}.py"

        with open(os.path.join(os.getcwd(), migration_directory, file_name), "w") as fp:
            fp.write(output)

        self.info(f"Migration file created: {file_name}")
