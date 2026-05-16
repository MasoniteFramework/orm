"""CreateProductStoreTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateProductStoreTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("product_store") as table:
            table.increments("id").primary()
            table.integer("product_id")
            table.integer("store_id")
            table.timestamps()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("product_store")
