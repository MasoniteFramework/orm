"""CreateTableSchemaMigration Migration."""

from src.masoniteorm.migrations import Migration


class CreateTableSchemaMigration(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("table_schema") as table:
            table.increments('id')
            table.string('name')
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("table_schema")
