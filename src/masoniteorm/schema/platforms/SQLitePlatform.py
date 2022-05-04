from ..Table import Table
from .Platform import Platform


class SQLitePlatform(Platform):

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
        "big_increments": "BIGINT",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "integer_unsigned": "INT UNSIGNED",
        "big_integer_unsigned": "BIGINT UNSIGNED",
        "tiny_integer_unsigned": "TINYINT UNSIGNED",
        "small_integer_unsigned": "SMALLINT UNSIGNED",
        "medium_integer_unsigned": "MEDIUMINT UNSIGNED",
        "increments": "INTEGER",
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
        "timestamp": "TIMESTAMP",
        "date": "DATE",
        "year": "VARCHAR",
        "datetime": "DATETIME",
        "tiny_increments": "TINYINT AUTO_INCREMENT",
        "unsigned": "INT UNSIGNED",
    }

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT NOW()",
        "null": " DEFAULT NULL",
    }

    premapped_nulls = {True: "NULL", False: "NOT NULL"}

    def compile_create_sql(self, table, if_not_exists=False):
        sql = []
        table_create_format = (
            self.create_if_not_exists_format()
            if if_not_exists
            else self.create_format()
        )
        sql.append(
            table_create_format.format(
                table=self.get_table_string().format(table=table.name).strip(),
                columns=", ".join(self.columnize(table.get_added_columns())).strip(),
                constraints=", "
                + ", ".join(self.constraintize(table.get_added_constraints()))
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
                    f"CREATE INDEX {index.name} ON {self.wrap_table(table.name)}({','.join(index.column)})"
                )

        return sql

    def columnize(self, columns):
        sql = []
        for name, column in columns.items():
            if column.length:
                length = self.create_column_length(column.column_type).format(
                    length=column.length
                )
            else:
                length = ""

            if column.default == "":
                default = " DEFAULT ''"
            elif column.default in (0,):
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
                constraint = "PRIMARY KEY"

            if column.column_type == "enum":
                values = ", ".join(f"'{x}'" for x in column.values)
                column_constraint = f" CHECK({column.name} IN ({values}))"

            sql.append(
                self.columnize_string()
                .format(
                    name=self.wrap_column(column.name),
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

    def compile_alter_sql(self, diff):
        sql = []

        if diff.removed_indexes or diff.removed_unique_indexes:
            indexes = diff.removed_indexes
            indexes += diff.removed_unique_indexes
            for name in indexes:
                sql.append("DROP INDEX {name}".format(name=name))

        if diff.added_columns:
            for name, column in diff.added_columns.items():
                default = ""
                if column.default in (0,):
                    default = f" DEFAULT {column.default}"
                elif column.default in self.premapped_defaults.keys():
                    default = self.premapped_defaults.get(column.default)
                elif column.default:
                    if isinstance(column.default, (str,)):
                        default = f" DEFAULT '{column.default}'"
                    else:
                        default = f" DEFAULT {column.default}"
                else:
                    default = ""
                constraint = ""
                if column.name in diff.added_foreign_keys:
                    foreign_key = diff.added_foreign_keys[column.name]
                    constraint = f" REFERENCES {self.wrap_table(foreign_key.foreign_table)}({self.wrap_column(foreign_key.foreign_column)})"

                sql.append(
                    "ALTER TABLE {table} ADD COLUMN {name} {data_type} {nullable}{default}{constraint}".format(
                        table=self.wrap_table(diff.name),
                        name=self.wrap_column(column.name),
                        data_type=self.type_map.get(column.column_type, ""),
                        nullable="NULL" if column.is_null else "NOT NULL",
                        default=default,
                        constraint=constraint,
                    ).strip()
                )
        if (
            diff.renamed_columns
            or diff.dropped_columns
            or diff.changed_columns
            or diff.added_foreign_keys
        ):
            original_columns = diff.from_table.added_columns
            # pop off the dropped columns. No need for them here
            for column in diff.dropped_columns:
                original_columns.pop(column)

            sql.append(
                "CREATE TEMPORARY TABLE __temp__{table} AS SELECT {original_column_names} FROM {table}".format(
                    table=diff.name,
                    original_column_names=", ".join(
                        diff.from_table.added_columns.keys()
                    ),
                )
            )

            sql.append("DROP TABLE {table}".format(table=self.wrap_table(diff.name)))

            columns = diff.from_table.added_columns

            columns.update(diff.renamed_columns)
            columns.update(diff.changed_columns)
            columns.update(diff.added_columns)

            sql.append(
                self.create_format().format(
                    table=self.get_table_string().format(table=diff.name).strip(),
                    columns=", ".join(self.columnize(columns)).strip(),
                    constraints=", "
                    + ", ".join(self.constraintize(diff.get_added_constraints()))
                    if diff.get_added_constraints()
                    else "",
                    foreign_keys=", "
                    + ", ".join(
                        self.foreign_key_constraintize(
                            diff.name, diff.added_foreign_keys
                        )
                    )
                    if diff.added_foreign_keys
                    else "",
                )
            )

            for column in diff.added_columns:
                columns.pop(column)

            sql.append(
                "INSERT INTO {quoted_table} ({new_columns}) SELECT {original_column_names} FROM __temp__{table}".format(
                    quoted_table=self.wrap_table(diff.name),
                    table=diff.name,
                    new_columns=", ".join(self.columnize_names(columns)),
                    original_column_names=", ".join(
                        diff.from_table.added_columns.keys()
                    ),
                )
            )
            sql.append("DROP TABLE __temp__{table}".format(table=diff.name))

        if diff.new_name:
            sql.append(
                "ALTER TABLE {old_name} RENAME TO {new_name}".format(
                    old_name=self.wrap_table(diff.name),
                    new_name=self.wrap_table(diff.new_name),
                )
            )

        if diff.added_indexes:
            for name, index in diff.added_indexes.items():
                sql.append(
                    f"CREATE INDEX {index.name} ON {self.wrap_table(diff.name)}({','.join(index.column)})"
                )
        if diff.added_constraints:
            for name, constraint in diff.added_constraints.items():
                if constraint.constraint_type == "unique":
                    sql.append(
                        f"CREATE UNIQUE INDEX {constraint.name} ON {self.wrap_table(diff.name)}({','.join(constraint.columns if isinstance(constraint.columns, list) else [constraint.columns])})"
                    )
                elif constraint.constraint_type == "primary_key":
                    sql.append(
                        f"ALTER TABLE {self.wrap_table(diff.name)} ADD CONSTRAINT {constraint.name} PRIMARY KEY ({','.join(constraint.columns)})"
                    )

        return sql

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints}{foreign_keys})"

    def create_if_not_exists_format(self):
        return (
            "CREATE TABLE IF NOT EXISTS {table} ({columns}{constraints}{foreign_keys})"
        )

    def get_table_string(self):
        return '"{table}"'

    def get_column_string(self):
        return '"{column}"'

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

    def columnize_string(self):
        return "{name} {data_type}{length}{column_constraint} {nullable}{default} {constraint}"

    def get_unique_constraint_string(self):
        return "UNIQUE({columns})"

    def get_foreign_key_constraint_string(self):
        return "CONSTRAINT {constraint_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}){cascade}"

    def get_primary_key_constraint_string(self):
        return "CONSTRAINT {constraint_name} PRIMARY KEY ({columns})"

    def constraintize(self, constraints):
        sql = []
        for name, constraint in constraints.items():
            sql.append(
                getattr(
                    self, f"get_{constraint.constraint_type}_constraint_string"
                )().format(
                    columns=", ".join(constraint.columns),
                    constraint_name=constraint.name,
                )
            )
        return sql

    def foreign_key_constraintize(self, table, foreign_keys):
        sql = []
        for name, foreign_key in foreign_keys.items():
            cascade = ""
            if foreign_key.delete_action:
                cascade += f" ON DELETE {self.foreign_key_actions.get(foreign_key.delete_action.lower())}"
            if foreign_key.update_action:
                cascade += f" ON UPDATE {self.foreign_key_actions.get(foreign_key.update_action.lower())}"
            sql.append(
                self.get_foreign_key_constraint_string().format(
                    column=self.wrap_column(foreign_key.column),
                    constraint_name=foreign_key.constraint_name,
                    table=self.wrap_table(table),
                    foreign_table=self.wrap_table(foreign_key.foreign_table),
                    foreign_column=self.wrap_column(foreign_key.foreign_column),
                    cascade=cascade,
                )
            )
        return sql

    def columnize_names(self, columns):
        names = []
        for name, column in columns.items():
            names.append(self.wrap_column(column.name))

        return names

    def get_current_schema(self, connection, table_name):
        sql = f"PRAGMA table_info({table_name})"

        reversed_type_map = {v: k for k, v in self.type_map.items()}
        table = Table(table_name)

        result = connection.query(sql, ())
        for column in result:
            default = column.get("dflt_value")
            if default:
                default = default.replace("'", "")

            table.add_column(
                column["name"], reversed_type_map.get(column["type"]), default=default
            )
            if column.get("pk") == 1:
                table.set_primary_key(column["name"])

        return table

    def compile_table_exists(self, table, database=None):
        return f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"

    def compile_column_exists(self, table, column):
        return f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' and column_name='{column}'"

    def compile_truncate(self, table, foreign_keys=False):
        if not foreign_keys:
            return f"DELETE FROM {self.wrap_table(table)}"

        return [
            self.disable_foreign_key_constraints(),
            f"DELETE FROM {self.wrap_table(table)}",
            self.enable_foreign_key_constraints(),
        ]

    def compile_rename_table(self, current_table, new_name):
        return f"ALTER TABLE {self.wrap_table(current_table)} RENAME TO {self.wrap_table(new_name)}"

    def compile_drop_table_if_exists(self, current_table):
        return f"DROP TABLE IF EXISTS {self.wrap_table(current_table)}"

    def compile_drop_table(self, current_table):
        return f"DROP TABLE {self.wrap_table(current_table)}"

    def enable_foreign_key_constraints(self):
        return "PRAGMA foreign_keys = ON"

    def disable_foreign_key_constraints(self):
        return "PRAGMA foreign_keys = OFF"
