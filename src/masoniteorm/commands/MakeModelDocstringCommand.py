from ..config import load_config
from .Command import Command


class MakeModelDocstringCommand(Command):
    """
    Generate model docstring and type hints (for auto-completion).

    model:docstring
        {table : The table you want to generate docstring and type hints}
        {--c|connection=default : The connection you want to use}
    """

    def handle(self):
        table = self.argument("table")
        DB = load_config(self.option("config")).DB

        if self.option("connection") == "default":
            schema = DB.get_schema_builder()
        else:
            schema = DB.get_schema_builder(self.option("connection"))

        if not schema.has_table(table):
            return self.line_error(
                f"There is no such table {table} for this connection."
            )

        self.info(f"Model Docstring for table: {table}")
        for name, column in schema.get_columns(table):
            length = f"({column.length})" if column.length else ""
            default = f" default: {column.default}"
            print(f"{column.name}: {column.column_type}{length}{default}")

        self.info(f"Model Type Hints for table: {table}")
        for name, column in schema.get_columns(table):
            print(f"    {name}:{column.column_python_type.__name__}")
