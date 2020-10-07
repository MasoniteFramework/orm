

class SQLitePlatform:

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INTEGER",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "BIGINT",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "INTEGER PRIMARY KEY",
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
        "unsigned_integer": "UNSIGNED INT",
    }

    def compile_create_sql(self, table):
        columns = self.columnize(table.get_added_columns())
        
        return self.create_format().format(
            table=self.table_string().format(table=table.name).strip(),
            columns=', '.join(self.columnize(table.get_added_columns())).strip(),
            constraints=', ' + ', '.join(self.constraintize(table.get_added_constraints())) if table.get_added_constraints() else ""
        )

    def compile_alter_sql(self, diff):
        sql = []

        if diff.new_name:
            sql.append("ALTER TABLE {old_name} RENAME TO {new_name}".format(old_name=diff.name, new_name=diff.new_name))

        return sql

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints})"

    def table_string(self):
        return '"{table}"'

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

    def columnize_string(self):
        return "{name} {data_type}{length} {constraint}"

    def get_unique_constraint_string(self):
        return "UNIQUE({columns})"

    def constraintize(self, constraints):
        sql = []
        for name, constraint in constraints.items():
            print('cc', constraint.columns)
            sql.append(
                getattr(self, f"get_{constraint.constraint_type}_constraint_string")().format(
                    columns=', '.join(constraint.columns)
                )
            )
            print(constraint)
        return sql

    def columnize(self, columns):
        sql = []
        for name, column in columns.items():
            if column.length:
                length = self.create_column_length(column.column_type).format(length=column.length)
            else:
                length = ""
            sql.append(self.columnize_string().format(
                name=column.name,
                data_type=self.type_map.get(column.column_type, ""),
                length=length,
                constraint="PRIMARY KEY" if column.primary else ""
                # nullable=self.null_map.get(column.is_null) or ""
            ).strip())
        
        return sql
