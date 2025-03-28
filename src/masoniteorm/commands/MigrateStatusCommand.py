from ..migrations import Migration
from .Command import Command


class MigrateStatusCommand(Command):
    """
    Display migrations status.

    migrate:status
        {--c|connection=default : The connection you want to run migrations on}
        {--schema=? : Sets the schema to be migrated}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

    def handle(self):
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
            schema=self.option("schema"),
        )
        migration.create_table_if_not_exists()
        table = self.table()
        table.set_header_row(["Ran?", "Migration", "Batch"])
        migrations = []

        for migration_data in migration.get_ran_migrations():
            migration_file = migration_data["migration_file"]
            batch = migration_data["batch"]

            migrations.append(
                [
                    "<info>Y</info>",
                    f"<comment>{migration_file}</comment>",
                    f"<info>{batch}</info>",
                ]
            )

        for migration_file in migration.get_unran_migrations():
            migrations.append(
                [
                    "<error>N</error>",
                    f"<comment>{migration_file}</comment>",
                    "<info>-</info>",
                ]
            )

        table.set_rows(migrations)

        table.render(self.io)
