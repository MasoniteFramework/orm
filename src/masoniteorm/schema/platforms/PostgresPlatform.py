from .Platform import Platform


class PostgresPlatform(Platform):
    types_without_lengths = ["integer"]

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
        "binary": "LONGBLOB",
        "boolean": "BOOLEAN",
        "decimal": "DECIMAL",
        "double": "DOUBLE",
        "enum": "VARCHAR(255) CHECK ",
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
        "datetime": "TIMESTAMP",
        "tiny_increments": "TINYINT AUTO_INCREMENT",
        "unsigned": "INT",
        "unsigned_integer": "INT",
    }

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
        return "CONSTRAINT {column}_{table}_{foreign_table}_{foreign_column}_foreign FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column})"

    def get_unique_constraint_string(self):
        return "CONSTRAINT {table}_{name_columns}_unique UNIQUE ({columns})"

    def get_table_string(self):
        return '"{table}"'
