from cleo import Command
import os
from ..migrations import Migration


class MigrateStatusCommand(Command):
    """
    Display migrations status.

    migrate:status
        {--c|connection=default : The connection you want to run migrations on}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        from config.database import ConnectionResolver

        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
        )
        migration.create_table_if_not_exists()
        table = self.table()
        table.set_header_row(["Ran?", "Migration"])
        migrations = []

        for migration_file in migration.get_ran_migrations():
            migrations.append(
                ["<info>Y</info>", f"<comment>{migration_file}</comment>"]
            )

        for migration_file in migration.get_unran_migrations():
            migrations.append(
                ["<error>N</error>", f"<comment>{migration_file}</comment>"]
            )

        table.set_rows(migrations)

        table.render(self.io)
