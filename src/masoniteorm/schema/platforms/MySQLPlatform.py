from .Platform import Platform
from ..Table import Table


class MySQLPlatform(Platform):
    types_without_lengths = ["enum"]

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INT",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "BIGINT AUTO_INCREMENT",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY",
        "uuid": "CHAR",
        "binary": "LONGBLOB",
        "boolean": "BOOLEAN",
        "decimal": "DECIMAL",
        "double": "DOUBLE",
        "enum": "ENUM",
        "text": "TEXT",
        "float": "FLOAT",
        "geometry": "GEOMETRY",
        "json": "JSON",
        "jsonb": "LONGBLOB",
        "long_text": "LONGTEXT",
        "point": "POINT",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "date": "DATE",
        "year": "YEAR",
        "datetime": "DATETIME",
        "tiny_increments": "TINYINT AUTO_INCREMENT",
        "unsigned": "INT UNSIGNED",
        "unsigned_integer": "INT UNSIGNED",
    }

    premapped_nulls = {True: "NULL", False: "NOT NULL"}

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT NOW()",
        "null": " DEFAULT NULL",
    }

    def columnize(self, columns):
        sql = []
        for name, column in columns.items():
            if column.length:
                length = self.create_column_length(column.column_type).format(
                    length=column.length
                )
            else:
                length = ""

            if column.default in (0,):
                default = f" DEFAULT {column.default}"
            elif column.default in self.premapped_defaults:
                default = self.premapped_defaults.get(column.default)
            elif column.default:
                if isinstance(column.default, (str,)):
                    default = f" DEFAULT '{column.default}'"
                else:
                    default = f" DEFAULT {column.default}"
            else:
                default = ""

            constraint = ""
            column_constraint = ""
            if column.primary:
                constraint = "PRIMARY KEY"

            if column.column_type == "enum":
                values = ", ".join(f"'{x}'" for x in column.values)
                column_constraint = f"({values})"

            sql.append(
                self.columnize_string()
                .format(
                    name=column.name,
                    data_type=self.type_map.get(column.column_type, ""),
                    column_constraint=column_constraint,
                    length=length,
                    constraint=constraint,
                    nullable=self.premapped_nulls.get(column.is_null) or "",
                    default=default,
                )
                .strip()
            )

        return sql

    def compile_create_sql(self, table):
        sql = []

        sql.append(
            self.create_format().format(
                table=table.name,
                columns=", ".join(self.columnize(table.get_added_columns())).strip(),
                constraints=", "
                + ", ".join(self.constraintize(table.get_added_constraints(), table))
                if table.get_added_constraints()
                else "",
                foreign_keys=", "
                + ", ".join(
                    self.foreign_key_constraintize(table.name, table.added_foreign_keys)
                )
                if table.added_foreign_keys
                else "",
            )
        )

        return sql[0]

    def compile_alter_sql(self, table):
        sql = []

        if table.added_columns:
            add_columns = []

            for name, column in table.get_added_columns().items():
                if column.length:
                    length = self.create_column_length(column.column_type).format(
                        length=column.length
                    )
                else:
                    length = ""

                add_columns.append(
                    self.add_column_string()
                    .format(
                        name=column.name,
                        data_type=self.type_map.get(column.column_type, ""),
                        length=length,
                        constraint="PRIMARY KEY" if column.primary else "",
                        nullable="NULL" if column.is_null else "NOT NULL",
                    )
                    .strip()
                )

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns=", ".join(add_columns).strip(),
                )
            )

        if table.renamed_columns:
            renamed_sql = []

            for name, column in table.get_renamed_columns().items():
                if column.length:
                    length = self.create_column_length(column.column_type).format(
                        length=column.length
                    )
                else:
                    length = ""

                renamed_sql.append(
                    self.rename_column_string().format(to=column.name, old=name).strip()
                )

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns=", ".join(renamed_sql).strip(),
                )
            )

        if table.changed_columns:

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns="MODIFY "
                    + ", ".join(self.columnize(table.changed_columns)),
                )
            )

        if table.dropped_columns:
            dropped_sql = []

            for name in table.get_dropped_columns():
                dropped_sql.append(self.drop_column_string().format(name=name).strip())

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name), columns=", ".join(dropped_sql)
                )
            )

        if table.added_foreign_keys:
            for (
                column,
                foreign_key_constraint,
            ) in table.get_added_foreign_keys().items():
                sql.append(
                    f"ALTER TABLE {self.wrap_table(table.name)} ADD "
                    + self.get_foreign_key_constraint_string().format(
                        column=column,
                        table=table.name,
                        foreign_table=foreign_key_constraint.foreign_table,
                        foreign_column=foreign_key_constraint.foreign_column,
                    )
                )

        if table.dropped_foreign_keys:
            constraints = table.dropped_foreign_keys
            for constraint in constraints:
                sql.append(
                    f"ALTER TABLE {self.wrap_table(table.name)} DROP FOREIGN KEY {constraint}"
                )

        if table.added_indexes:
            for name, index in table.added_indexes.items():
                sql.append(
                    "CREATE INDEX {name} ON {table}({column})".format(
                        name=index.name, table=table.name, column=index.column
                    )
                )

        if table.removed_indexes:
            constraints = table.removed_indexes
            for constraint in constraints:
                sql.append(
                    f"ALTER TABLE {self.wrap_table(table.name)} DROP INDEX {constraint}"
                )

        return sql

    def add_column_string(self):
        return "ADD {name} {data_type}{length} {nullable}"

    def drop_column_string(self):
        return "DROP COLUMN {name}"

    def change_column_string(self):
        return "MODIFY {name}{data_type}{length} {nullable}{default} {constraint}"

    def rename_column_string(self):
        return "RENAME COLUMN {old} TO {to}"

    def columnize_string(self):
        return "{name} {data_type}{length}{column_constraint} {nullable}{default} {constraint}"

    def constraintize(self, constraints, table):
        sql = []
        for name, constraint in constraints.items():
            sql.append(
                getattr(
                    self, f"get_{constraint.constraint_type}_constraint_string"
                )().format(
                    columns=", ".join(constraint.columns),
                    name_columns="_".join(constraint.columns),
                    table=table.name,
                )
            )

        return sql

    def get_table_string(self):
        return "`{table}`"

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints}{foreign_keys})"

    def alter_format(self):
        return "ALTER TABLE {table} {columns}"

    def get_foreign_key_constraint_string(self):
        return "CONSTRAINT {table}_{column}_foreign FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column})"

    def get_unique_constraint_string(self):
        return "CONSTRAINT {table}_{name_columns}_unique UNIQUE ({columns})"

    def compile_table_exists(self, table, database):
        return f"SELECT * from information_schema.tables where table_name='{table}' AND table_schema = '{database}'"

    def compile_truncate(self, table, foreign_keys=False):
        if not foreign_keys:
            return f"TRUNCATE {self.wrap_table(table)}"

        return [
            self.disable_foreign_key_constraints(),
            f"TRUNCATE {self.wrap_table(table)}",
            self.enable_foreign_key_constraints(),
        ]

    def compile_rename_table(self, current_name, new_name):
        return f"ALTER TABLE {self.wrap_table(current_name)} RENAME TO {self.wrap_table(new_name)}"

    def compile_drop_table_if_exists(self, table):
        return f"DROP TABLE IF EXISTS {self.wrap_table(table)}"

    def compile_drop_table(self, table):
        return f"DROP TABLE {self.wrap_table(table)}"

    def compile_column_exists(self, table, column):
        return f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' and column_name='{column}'"

    def get_current_schema(self, connection, table_name):
        return Table(table_name)

    def enable_foreign_key_constraints(self):
        return "SET FOREIGN_KEY_CHECKS=1"

    def disable_foreign_key_constraints(self):
        return "SET FOREIGN_KEY_CHECKS=0"
