from cleo import Command


class ModelDocstringCommand(Command):
    """
    Generate a model docstring based on a table definition
    model:docstring
        {table : Name of the table to generate the docstring for}
        {--c|connection=default : The connection to use}
    """

    def handle(self):
        from config.database import DB

        if self.option("connection") == "default":
            table_information = DB.get_schema_builder().list_table_columns(
                self.argument("table")
            )

        else:
            table_information = DB.get_schema_builder(
                self.option("connection")
            ).list_table_columns(self.argument("table"))

        docstring = '"""Model Definition (generated with love by Masonite) \n\n'
        for column_information in table_information:
            docstring += column_information + "\n"

        print(docstring + '"""')
