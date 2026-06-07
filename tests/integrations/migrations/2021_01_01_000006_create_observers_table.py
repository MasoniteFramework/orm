"""CreateObserversTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateObserversTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("observers") as table:
            table.increments("id").primary()
            table.string("name").nullable()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("observers")
