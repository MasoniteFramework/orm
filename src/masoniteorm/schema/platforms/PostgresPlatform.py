from .Platform import Platform
from ..Table import Table


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

    table_info_map = {"CHARACTER VARYING": "string"}

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
                    )
                    .strip()
                )

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns=", ".join(add_columns).strip(),
                    constraints=", "
                    + ", ".join(
                        self.constraintize(table.get_added_constraints(), table)
                    )
                    if table.get_added_constraints()
                    else "",
                    foreign_keys=", "
                    + ", ".join(
                        self.foreign_key_constraintize(
                            table.name, table.added_foreign_keys
                        )
                    )
                    if table.added_foreign_keys
                    else "",
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
                    self.rename_column_string()
                    .format(
                        to=column.name,
                        old=name,
                    )
                    .strip()
                )

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns=", ".join(renamed_sql).strip(),
                    constraints=", "
                    + ", ".join(
                        self.constraintize(table.get_added_constraints(), table)
                    )
                    if table.get_added_constraints()
                    else "",
                    foreign_keys=", "
                    + ", ".join(
                        self.foreign_key_constraintize(
                            table.name, table.added_foreign_keys
                        )
                    )
                    if table.added_foreign_keys
                    else "",
                )
            )

        if table.dropped_columns:
            dropped_sql = []

            for name in table.get_dropped_columns():
                dropped_sql.append(self.drop_column_string().format(name=name).strip())

            sql.append(
                self.alter_format().format(
                    table=self.wrap_table(table.name),
                    columns=", ".join(dropped_sql),
                    constraints=", "
                    + ", ".join(
                        self.constraintize(table.get_added_constraints(), table)
                    )
                    if table.get_added_constraints()
                    else "",
                    foreign_keys=", "
                    + ", ".join(
                        self.foreign_key_constraintize(
                            table.name, table.added_foreign_keys
                        )
                    )
                    if table.added_foreign_keys
                    else "",
                )
            )

        return sql

    def alter_format(self):
        return "ALTER TABLE {table} {columns}{constraints}{foreign_keys}"

    def add_column_string(self):
        return "ADD COLUMN {name} {data_type}{length} {constraint}"

    def drop_column_string(self):
        return "DROP COLUMN {name}"

    def rename_column_string(self):
        return "RENAME COLUMN {old} TO {to}"

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

    def table_information_string(self):
        return "SELECT * FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table}'"

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
