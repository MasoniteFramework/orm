from .Platform import Platform
from ..Table import Table


class MSSQLPlatform(Platform):

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
        "integer": "INT",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "BIGINT IDENTITY",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "INT IDENTITY",
        "uuid": "CHAR",
        "binary": "LONGBLOB",
        "boolean": "BOOLEAN",
        "decimal": "DECIMAL",
        "double": "DOUBLE",
        "enum": "VARCHAR",
        "text": "TEXT",
        "float": "FLOAT",
        "geometry": "GEOMETRY",
        "json": "JSON",
        "jsonb": "LONGBLOB",
        "inet": "VARCHAR",
        "cidr": "VARCHAR",
        "macaddr": "VARCHAR",
        "long_text": "LONGTEXT",
        "point": "POINT",
        "time": "TIME",
        "timestamp": "DATETIME",
        "date": "DATE",
        "year": "YEAR",
        "datetime": "DATETIME",
        "tiny_increments": "TINYINT IDENTITY",
        "unsigned": "INT",
        "unsigned_integer": "INT",
    }

    premapped_nulls = {True: "NULL", False: "NOT NULL"}

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT NOW()",
        "null": " DEFAULT NULL",
    }

    def compile_create_sql(self, table, if_not_exists=False):
        sql = []
        table_create_format = (
            self.create_if_not_exists_format()
            if if_not_exists
            else self.create_format()
        )
        sql.append(
            table_create_format.format(
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

        if table.added_indexes:
            for name, index in table.added_indexes.items():
                sql.append(
                    "CREATE INDEX {name} ON {table}({column})".format(
                        name=index.name,
                        table=self.wrap_table(table.name),
                        column=",".join(index.column),
                    )
                )

        return sql

    def compile_alter_sql(self, table):
        sql = []

        if table.added_columns:
            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns="ADD "
                    + ", ".join(self.columnize(table.added_columns)).strip(),
                )
            )

        if table.changed_columns:
            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns="ALTER COLUMN "
                    + ", ".join(self.columnize(table.changed_columns)).strip(),
                )
            )

        if table.renamed_columns:
            for name, column in table.get_renamed_columns().items():

                sql.append(
                    self.rename_column_string(table.name, name, column.name).strip()
                )

        if table.dropped_columns:
            dropped_sql = []

            for name in table.get_dropped_columns():
                dropped_sql.append(self.drop_column_string().format(name=name).strip())

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns="DROP COLUMN " + ", ".join(dropped_sql),
                )
            )

        if table.added_foreign_keys:
            for (
                column,
                foreign_key_constraint,
            ) in table.get_added_foreign_keys().items():
                cascade = ""
                if foreign_key_constraint.delete_action:
                    cascade += f" ON DELETE {self.foreign_key_actions.get(foreign_key_constraint.delete_action.lower())}"
                if foreign_key_constraint.update_action:
                    cascade += f" ON UPDATE {self.foreign_key_actions.get(foreign_key_constraint.update_action.lower())}"
                sql.append(
                    f"ALTER TABLE {self.wrap_table(table.name)} ADD "
                    + self.get_foreign_key_constraint_string().format(
                        constraint_name=foreign_key_constraint.constraint_name,
                        column=self.wrap_column(column),
                        table=self.wrap_table(table.name),
                        foreign_table=self.wrap_table(
                            foreign_key_constraint.foreign_table
                        ),
                        foreign_column=self.wrap_column(
                            foreign_key_constraint.foreign_column
                        ),
                        cascade=cascade,
                    )
                )

        if table.dropped_foreign_keys:
            constraints = table.dropped_foreign_keys
            for constraint in constraints:
                sql.append(
                    f"ALTER TABLE {self.wrap_table(table.name)} DROP CONSTRAINT {constraint}"
                )

        if table.added_indexes:
            for name, index in table.added_indexes.items():
                sql.append(
                    "CREATE INDEX {name} ON {table}({column})".format(
                        name=index.name,
                        table=self.wrap_table(table.name),
                        column=",".join(index.column),
                    )
                )

        if (
            table.removed_indexes
            or table.removed_unique_indexes
            or table.dropped_primary_keys
        ):
            constraints = table.removed_indexes
            constraints += table.removed_unique_indexes
            constraints += table.dropped_primary_keys
            for constraint in constraints:
                sql.append(
                    f"DROP INDEX {self.wrap_table(table.name)}.{self.wrap_table(constraint)}"
                )

        if table.added_constraints:
            for name, constraint in table.added_constraints.items():
                if constraint.constraint_type == "unique":
                    sql.append(
                        f"ALTER TABLE {self.wrap_table(table.name)} ADD CONSTRAINT {constraint.name} UNIQUE({','.join(constraint.columns)})"
                    )
                elif constraint.constraint_type == "fulltext":
                    pass
                elif constraint.constraint_type == "primary_key":
                    sql.append(
                        f"ALTER TABLE {self.wrap_table(table.name)} ADD CONSTRAINT {constraint.name} PRIMARY KEY ({','.join(constraint.columns)})"
                    )
        return sql

    def add_column_string(self):
        return "{name} {data_type}{length}"

    def drop_column_string(self):
        return "{name}"

    def rename_column_string(self, table, old, new):
        return f"EXEC sp_rename '{table}.{old}', '{new}', 'COLUMN'"

    def columnize(self, columns):
        sql = []
        for name, column in columns.items():
            if column.length:
                length = self.create_column_length(column.column_type).format(
                    length=column.length
                )
            else:
                length = ""

            default = ""
            if column.default in (0,):
                default = f" DEFAULT {column.default}"
            elif column.default in self.premapped_defaults.keys():
                default = self.premapped_defaults.get(column.default)
            elif column.default:
                if isinstance(column.default, (str,)) and not column.default_is_raw:
                    default = f" DEFAULT '{column.default}'"
                else:
                    default = f" DEFAULT {column.default}"
            else:
                default = ""

            constraint = ""
            column_constraint = ""
            if column.primary:
                constraint = " PRIMARY KEY"

            if column.column_type == "enum":
                values = ", ".join(f"'{x}'" for x in column.values)
                column_constraint = f" CHECK([{column.name}] IN ({values}))"

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

    def columnize_string(self):
        return "[{name}] {data_type}{length} {nullable}{default}{column_constraint}{constraint}"

    def constraintize(self, constraints, table):
        sql = []
        for name, constraint in constraints.items():
            sql.append(
                getattr(
                    self, f"get_{constraint.constraint_type}_constraint_string"
                )().format(
                    columns=", ".join(constraint.columns),
                    name_columns="_".join(constraint.columns),
                    constraint_name=constraint.name,
                    table=table.name,
                )
            )

        return sql

    def get_table_string(self):
        return "[{table}]"

    def get_column_string(self):
        return "[{column}]"

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints}{foreign_keys})"

    def create_if_not_exists_format(self):
        return (
            "CREATE TABLE IF NOT EXISTS {table} ({columns}{constraints}{foreign_keys})"
        )

    def alter_format(self):
        return "ALTER TABLE {table} {columns}"

    def get_foreign_key_constraint_string(self):
        return "CONSTRAINT {constraint_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}){cascade}"

    def get_primary_key_constraint_string(self):
        return "CONSTRAINT {constraint_name} PRIMARY KEY ({columns})"

    def get_unique_constraint_string(self):
        return "CONSTRAINT {constraint_name} UNIQUE ({columns})"

    def compile_table_exists(self, table, database):
        return f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table}'"

    def compile_truncate(self, table, foreign_keys=False):
        if not foreign_keys:
            return f"TRUNCATE TABLE {self.wrap_table(table)}"

        return [
            f"ALTER TABLE {self.wrap_table(table)} NOCHECK CONSTRAINT ALL",
            f"TRUNCATE TABLE {self.wrap_table(table)}",
            f"ALTER TABLE {self.wrap_table(table)} WITH CHECK CHECK CONSTRAINT ALL",
        ]

    def compile_rename_table(self, current_name, new_name):
        return f"EXEC sp_rename {self.wrap_table(current_name)}, {self.wrap_table(new_name)}"

    def compile_drop_table_if_exists(self, table):
        return f"DROP TABLE IF EXISTS {self.wrap_table(table)}"

    def compile_drop_table(self, table):
        return f"DROP TABLE {self.wrap_table(table)}"

    def compile_column_exists(self, table, column):
        return f"SELECT 1 FROM sys.columns WHERE Name = N'{column}' AND Object_ID = Object_ID(N'{table}')"

    def get_current_schema(self, connection, table_name):
        return Table(table_name)

    def enable_foreign_key_constraints(self):
        """MSSQL does not allow a global way to enable foreign key constraints"""
        return ""

    def disable_foreign_key_constraints(self):
        """MSSQL does not allow a global way to disable foreign key constraints"""
        return ""
