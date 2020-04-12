"""

Migrations needs to:
    * Maintain a migrations table
    * Generate migration files
"""

from src.masonite.orm.schema import Schema


class Migration:
    def __init__(self, connection="mysql"):
        self.schema = Schema.on(connection)

    def create_table_if_not_exists(self):
        print(self.schema.has_table("migrations"))

    def get_unran_migrations(self):
        pass

    def get_ran_migrations(self):
        pass

    def migrate(self):
        pass

    def rollback(self):
        pass

    def refresh(self):
        pass
