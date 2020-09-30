from cleo import Command
import os
from ..migrations import Migration


class MigrateCommand(Command):
    """
    Run migrations.

    migrate
        {--c|connection=default : The connection you want to run migrations on}
        {--f|force : Force migrations without prompt in production}
    """

    def handle(self):
        # prompt user for confirmation in production
        if os.getenv("APP_ENV") == "production" and not self.option("force"):
            answer = ""
            while answer not in ["y", "n"]:
                answer = input(
                    "Do you want to run migrations in PRODUCTION ? (y/n)\n"
                ).lower()
            if answer != "y":
                self.info("Migrations cancelled")
                exit(0)

        self.info("starting migration class")
        migration = Migration(command_class=self)
        self.info("creating table if not exists")
        migration.create_table_if_not_exists()
        if not migration.get_unran_migrations():
            self.info("Nothing to migrate")

        migration.migrate()
