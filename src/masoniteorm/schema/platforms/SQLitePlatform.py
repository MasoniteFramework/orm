

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

        if diff.removed_indexes:
            for name, index in diff.removed_indexes.items():
                sql.append("DROP INDEX {name}".format(name=index.name))

        if diff.new_name:
            sql.append("ALTER TABLE {old_name} RENAME TO {new_name}".format(old_name=diff.name, new_name=diff.new_name))
        
        if diff.added_columns:
            for name, column in diff.added_columns.items():
                sql.append("ALTER TABLE {table} ADD COLUMN {name} {data_type}".format(
                    table=diff.name, 
                    name=column.name,
                    data_type=self.type_map.get(column.column_type, ""),
                ).strip())
        
        if diff.renamed_columns:
            sql.append("CREATE TEMPORARY TABLE __temp__{table} AS SELECT {original_column_names} FROM {table}".format(
                table=diff.name,
                original_column_names=', '.join(diff.from_table.added_columns.keys())
            ))
            sql.append("DROP TABLE {table}".format(table=diff.name))
            sql.append(self.create_format().format(
                table=self.table_string().format(table=diff.name).strip(),
                columns=', '.join(self.columnize(diff.renamed_columns)).strip(),
                constraints=', ' + ', '.join(self.constraintize(diff.get_added_constraints())) if diff.get_added_constraints() else ""
            ))
            sql.append("INSERT INTO {quoted_table} (comment) SELECT {columns} FROM __temp__{table}".format(
                quoted_table=self.table_string().format(table=diff.name).strip(),
                table=diff.name,
                columns=', '.join(diff.renamed_columns.keys())
            ))
            sql.append("DROP TABLE __temp__{table}".format(
                table=diff.name
            ))

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
