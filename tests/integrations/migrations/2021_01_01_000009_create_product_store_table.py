"""CreateProductStoreTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateProductStoreTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("product_store") as table:
            table.increments("id").primary()
            table.integer("product_id")
            table.integer("store_id")
            # Pivot timestamps are checked explicitly in test_belongs_to_many.
            table.datetime("created_at").default("CURRENT_TIMESTAMP")
            table.datetime("updated_at").default("CURRENT_TIMESTAMP")

    def down(self):
        """Revert the migrations."""
        self.schema.drop("product_store")
