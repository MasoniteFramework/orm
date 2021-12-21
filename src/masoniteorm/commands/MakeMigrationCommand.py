import datetime
import os
import pathlib

from inflection import camelize, tableize

from .Command import Command


class MakeMigrationCommand(Command):
    """
    Creates a new migration file.

    migration
        {name : The name of the migration}
        {--c|create=None : The table to create}
        {--t|table=None : The table to alter}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        name = self.argument("name")
        now = datetime.datetime.today()

        if self.option("create") != "None":
            table = self.option("create")
            stub_file = "create_migration"
        else:
            table = self.option("table")
            stub_file = "table_migration"

        if table == "None":
            table = tableize(name.replace("create_", "").replace("_table", ""))
            stub_file = "create_migration"

        migration_directory = self.option("directory")

        with open(
            os.path.join(
                pathlib.Path(__file__).parent.absolute(), f"stubs/{stub_file}.stub"
            )
        ) as fp:
            output = fp.read()
            output = output.replace("__MIGRATION_NAME__", camelize(name))
            output = output.replace("__TABLE_NAME__", table)

        file_name = f"{now.strftime('%Y_%m_%d_%H%M%S')}_{name}.py"

        with open(os.path.join(os.getcwd(), migration_directory, file_name), "w") as fp:
            fp.write(output)

        self.info(
            f"Migration file created: {os.path.join(migration_directory, file_name)}"
        )
