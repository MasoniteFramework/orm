"""CreateProfilesTable Migration."""

from src.masoniteorm.migrations import Migration


class CreateProfilesTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("profiles") as table:
            table.increments("id").primary()
            table.integer("user_id")
            table.string("title").nullable()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("profiles")
