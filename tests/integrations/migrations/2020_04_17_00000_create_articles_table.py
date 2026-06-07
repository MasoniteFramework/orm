from src.masoniteorm.migrations.Migration import Migration


class CreateArticlesTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("articles") as table:
            table.increments("id").primary()
            table.integer("user_id")
            table.string("title").nullable()
            table.integer("status").nullable()
            table.datetime("published_date").nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("articles")
