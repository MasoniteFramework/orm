"""

Migrations needs to:
    * Maintain a migrations table
    * Generate migration files
"""
import os
from os import listdir, path
from os.path import isfile, join
from pydoc import locate

from inflection import camelize

from ..models.MigrationModel import MigrationModel
from ..schema import Schema


class Migration:
    def __init__(
        self,
        connection="mysql",
        dry=False,
        command_class=None,
        migration_directory="databases/migrations",
    ):
        self.schema = Schema.on(connection)
        self._dry = dry
        self.migration_directory = migration_directory.replace("/", ".")
        self.last_migrations_ran = []
        self.command_class = command_class

    def create_table_if_not_exists(self):
        if not self.schema.has_table("migrations"):
            with self.schema.create("migrations") as table:
                table.increments("migration_id")
                table.string("migration")
                table.integer("batch")

            return True

        return False

    def get_unran_migrations(self):
        directory_path = os.path.join(os.getcwd(), "databases/migrations")
        all_migrations = [
            f
            for f in listdir(directory_path)
            if isfile(join(directory_path, f)) and f != "__init__.py"
        ]
        unran_migrations = []
        database_migrations = MigrationModel.all()
        for migration in all_migrations:
            if migration.replace(".py", "") not in database_migrations.pluck(
                "migration"
            ):
                unran_migrations.append(migration)

        return unran_migrations

    def get_rollback_migrations(self):
        return (
            MigrationModel.where("batch", MigrationModel.all().max("batch"))
            .order_by("migration_id", "desc")
            .get()
            .pluck("migration")
        )

    def get_all_migrations(self, reverse=False):
        if reverse:
            return (
                MigrationModel.order_by("migration_id", "desc").get().pluck("migration")
            )

        return MigrationModel.all().pluck("migration")

    def get_last_batch_number(self):
        return MigrationModel.select("batch").get().max("batch")

    def delete_migration(self, file_path):
        return MigrationModel.where("migration", file_path).delete()

    def locate(self, file_name):
        migration_name = camelize("_".join(file_name.split("_")[4:]).replace(".py", ""))
        file_name = file_name.replace(".py", "")
        return locate(f"{self.migration_directory}.{file_name}.{migration_name}")

    def get_ran_migrations(self):
        pass

    def migrate(self):
        batch = self.get_last_batch_number() + 1
        for migration in self.get_unran_migrations():

            migration_module = migration.replace(".py", "")
            migration_name = camelize(
                "_".join(migration.split("_")[4:]).replace(".py", "")
            )
            migration_class = locate(
                f"{self.migration_directory}.{migration_module}.{migration_name}"
            )
            self.last_migrations_ran.append(migration)
            if self.command_class:
                self.command_class.line(
                    f"<comment>Migrating:</comment> <question>{migration}</question>"
                )

            migration_class().up()

            if self.command_class:
                self.command_class.line(
                    f"<info>Migrated:</info> <question>{migration}</question>"
                )

            MigrationModel.create({"batch": batch, "migration": migration})

    def rollback(self):
        for migration in self.get_rollback_migrations():
            if self.command_class:
                self.command_class.line(
                    f"<comment>Rolling back:</comment> <question>{migration}</question>"
                )

            self.locate(migration)().down()

            if self.command_class:
                self.command_class.line(
                    f"<info>Rolled back:</info> <question>{migration}</question>"
                )

        self.delete_last_batch()

    def rollback_all(self):
        ran_migrations = []
        for migration in self.get_all_migrations():
            self.locate(migration)().down()
            ran_migrations.append(migration)

        self.delete_migrations(ran_migrations)

    def delete_migrations(self, migrations=[]):
        return MigrationModel.where_in("migration", migrations).delete()

    def delete_last_batch(self):
        return MigrationModel.where("batch", self.get_last_batch_number()).delete()

    def refresh(self):
        for migration in self.get_all_migrations(reverse=True):
            if self.command_class:
                self.command_class.line(
                    f"<comment>Rolling back:</comment> <question>{migration}</question>"
                )

            self.locate(migration)().down()

            if self.command_class:
                self.command_class.line(
                    f"<info>Rolled back:</info> <question>{migration}</question>"
                )

            self.delete_migrations([migration])
        if self.command_class:
            self.command_class.line("")
        self.migrate()
