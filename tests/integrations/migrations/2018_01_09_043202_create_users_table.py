from src.masoniteorm.migrations import Migration


class CreateUsersTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("users") as table:
            table.increments("id").primary()
            table.string("name")
            table.string("email").unique().nullable()
            table.integer("age").nullable()
            table.boolean("is_admin").nullable()
            table.boolean("active").nullable()
            table.string("password").nullable()
            table.string("second_password").nullable()
            table.string("remember_token").nullable()
            table.timestamp("verified_at").nullable()
            table.timestamps()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("users")
