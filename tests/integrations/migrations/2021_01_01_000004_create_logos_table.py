"""CreateLogosTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateLogosTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("logos") as table:
            table.increments("id").primary()
            table.integer("article_id")
            table.string("url").nullable()
            table.datetime("published_date").nullable()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("logos")
