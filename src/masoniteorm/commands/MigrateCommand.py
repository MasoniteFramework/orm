from cleo import Command
import os
from ..migrations import Migration


class MigrateCommand(Command):
    """
    Run migrations.

    migrate
        {--c|connection=default : The connection you want to run migrations on}
        {--d|directory=databases/migrations : The location of the migration directory}
        {--f|force : Force migrations without prompt in production}
        {--s|show : Shows the output of SQL for migrations that would be running}
    """

    def handle(self):
        from config.database import DB

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

        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
        )
        migration.create_table_if_not_exists()
        if not migration.get_unran_migrations():
            self.info("Nothing To Migrate!")
            return

        migration.migrate(output=self.option("show"))
