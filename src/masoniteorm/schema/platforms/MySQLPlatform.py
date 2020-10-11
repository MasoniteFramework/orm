from .Platform import Platform


class MySQLPlatform(Platform):
    types_without_lengths = []

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

    def get_foreign_key_constraint_string(self):
        return "CONSTRAINT {table}_{column}_foreign FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column})"

    def get_unique_constraint_string(self):
        return "CONSTRAINT {table}_{name_columns}_unique UNIQUE ({columns})"

    def compile_table_exists(self, table):
        return f"SELECT * from information_schema.tables where table_name='{table}'"

    def compile_truncate(self, table):
        return f"TRUNCATE {self.wrap_table(table)}"

    def compile_rename_table(self, current_name, new_name):
        return f"ALTER TABLE {self.wrap_table(current_name)} RENAME TO {self.wrap_table(new_name)}"

    def compile_drop_table_if_exists(self, table):
        return f"DROP TABLE IF EXISTS {self.wrap_table(table)}"

    def compile_drop_table(self, table):
        return f"DROP TABLE {self.wrap_table(table)}"

    def compile_column_exists(self, table, column):
        return f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' and column_name='{column}'"
