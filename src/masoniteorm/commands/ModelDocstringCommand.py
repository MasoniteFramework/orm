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
            schema = DB.get_schema_builder()
        else:
            schema = DB.get_schema_builder(self.option("connection"))

        if not schema.has_table(self.argument("table")):
            return self.line_error(f"There's no such table {self.argument('table')} in this connection.")

        table_information = schema.list_table_columns(self.argument("table"))
        
        docstring = '\n"""Model Definition (generated with love by Masonite) \n'
        for column_information in table_information:
            docstring += column_information + "\n"

        print(docstring + '"""')
