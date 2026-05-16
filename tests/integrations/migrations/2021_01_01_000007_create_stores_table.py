"""CreateStoresTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateStoresTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("stores") as table:
            table.increments("id").primary()
            table.string("name")
            table.timestamps()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("stores")
