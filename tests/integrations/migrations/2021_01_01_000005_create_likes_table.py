"""CreateLikesTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateLikesTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("likes") as table:
            table.increments("id").primary()
            # Polymorphic columns: record_type holds the morph map key,
            # record_id holds the related model's PK.
            table.string("record_type", 63)
            table.integer("record_id")

    def down(self):
        """Revert the migrations."""
        self.schema.drop("likes")
