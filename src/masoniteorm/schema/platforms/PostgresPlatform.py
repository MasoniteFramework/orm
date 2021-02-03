from .Platform import Platform
from ..Table import Table


class PostgresPlatform(Platform):
    types_without_lengths = [
        "integer",
        "big_integer",
        "tiny_integer",
        "small_integer",
        "medium_integer",
    ]

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INTEGER",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "SERIAL UNIQUE",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "SERIAL UNIQUE",
        "uuid": "CHAR",
        "binary": "LONGBLOB",
        "boolean": "BOOLEAN",
        "decimal": "DECIMAL",
        "double": "DOUBLE PRECISION",
        "enum": "VARCHAR",
        "text": "TEXT",
        "float": "FLOAT",
        "geometry": "GEOMETRY",
        "json": "JSON",
        "jsonb": "JSONB",
        "long_text": "LONGTEXT",
        "point": "POINT",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "date": "DATE",
        "year": "YEAR",
        "datetime": "TIMESTAMP",
        "tiny_increments": "TINYINT AUTO_INCREMENT",
        "unsigned": "INT",
        "unsigned_integer": "INT",
    }

    table_info_map = {"CHARACTER VARYING": "string"}

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT NOW()",
        "null": " DEFAULT NULL",
    }

    premapped_nulls = {True: "NULL", False: "NOT NULL"}

    def compile_create_sql(self, table):
        sql = []

        sql.append(
            self.create_format().format(
                table=self.wrap_table(table.name),
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
                column_constraint = f" CHECK({column.name} IN ({values}))"

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

        if table.dropped_columns:
            dropped_sql = []

            for name in table.get_dropped_columns():
                dropped_sql.append(self.drop_column_string().format(name=name).strip())

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name), columns=", ".join(dropped_sql)
                )
            )

        if table.changed_columns:
            changed_sql = []

            for name, column in table.changed_columns.items():
                changed_sql.append(
                    self.modify_column_string()
                    .format(
                        name=name,
                        data_type=self.type_map.get(column.column_type),
                        nullable="NULL" if column.is_null else "NOT NULL",
                    )
                    .strip()
                )

                if column.is_null:
                    changed_sql.append(f"ALTER COLUMN {name} DROP NOT NULL")
                else:
                    changed_sql.append(f"ALTER COLUMN {name} SET NOT NULL")

                if column.default is not None:
                    changed_sql.append(
                        f"ALTER COLUMN {name} SET DEFAULT {column.default}"
                    )

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name), columns=", ".join(changed_sql)
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

        if table.dropped_foreign_keys or table.removed_indexes:
            constraints = table.dropped_foreign_keys
            constraints += table.removed_indexes
            for constraint in constraints:
                sql.append(
                    f"ALTER TABLE {self.wrap_table(table.name)} DROP CONSTRAINT {constraint}"
                )

        if table.added_indexes:
            for name, index in table.added_indexes.items():
                sql.append(
                    "CREATE INDEX {name} ON {table}({column})".format(
                        name=index.name, table=table.name, column=index.column
                    )
                )

        return sql

    def alter_format(self):
        return "ALTER TABLE {table} {columns}"

    def alter_format_add_foreign_key(self):
        return "ALTER TABLE {table} {columns}"

    def add_column_string(self):
        return "ADD COLUMN {name} {data_type}{length} {nullable} {constraint}"

    def drop_column_string(self):
        return "DROP COLUMN {name}"

    def modify_column_string(self):
        return "ALTER COLUMN {name} TYPE {data_type}"

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

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints}{foreign_keys})"

    def get_foreign_key_constraint_string(self):
        return "CONSTRAINT {table}_{column}_foreign FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column})"

    def get_unique_constraint_string(self):
        return "CONSTRAINT {table}_{name_columns}_unique UNIQUE ({columns})"

    def get_table_string(self):
        return '"{table}"'

    def table_information_string(self):
        return "SELECT * FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table}'"

    def compile_table_exists(self, table, database=None):
        return f"SELECT * from information_schema.tables where table_name='{table}'"

    def compile_truncate(self, table, foreign_keys=False):
        if not foreign_keys:
            return f"TRUNCATE {self.wrap_table(table)}"

        return [
            f"ALTER TABLE {self.wrap_table(table)} DISABLE TRIGGER ALL",
            f"TRUNCATE {self.wrap_table(table)}",
            f"ALTER TABLE {self.wrap_table(table)} ENABLE TRIGGER ALL",
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
        sql = self.table_information_string().format(table=table_name)

        reversed_type_map = {v: k for k, v in self.type_map.items()}
        reversed_type_map.update(self.table_info_map)
        table = Table(table_name)

        result = connection.query(sql, ())
        for column in result:
            table.add_column(
                column["column_name"],
                reversed_type_map.get(column["data_type"].upper()),
                default=column.get("dflt_value"),
            )
            column_default = column.get("column_default", "")
            if column_default and column_default.startswith("nextval"):
                table.set_primary_key(column["column_name"])

        return table

    def enable_foreign_key_constraints(self):
        """Postgres does not allow a global way to enable foreign key constraints
        """
        return ""

    def disable_foreign_key_constraints(self):
        """Postgres does not allow a global way to disable foreign key constraints
        """
        return ""
