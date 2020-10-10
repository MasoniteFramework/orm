class Platform:
    def columnize(self, columns):
        sql = []
        for name, column in columns.items():
            if column.length:
                length = self.create_column_length(column.column_type).format(
                    length=column.length
                )
            else:
                length = ""
            sql.append(
                self.columnize_string()
                .format(
                    name=column.name,
                    data_type=self.type_map.get(column.column_type, ""),
                    length=length,
                    constraint="PRIMARY KEY" if column.primary else ""
                    # nullable=self.null_map.get(column.is_null) or ""
                )
                .strip()
            )

        return sql

    def columnize_string(self):
        return "{name} {data_type}{length} {constraint}"

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

    def foreign_key_constraintize(self, table, foreign_keys):
        sql = []
        for name, foreign_key in foreign_keys.items():
            sql.append(
                self.get_foreign_key_constraint_string().format(
                    column=foreign_key.column,
                    table=table,
                    foreign_table=foreign_key.foreign_table,
                    foreign_column=foreign_key.foreign_column,
                )
            )
        return sql

    def constraintize(self, constraints):
        sql = []
        for name, constraint in constraints.items():
            sql.append(
                getattr(
                    self, f"get_{constraint.constraint_type}_constraint_string"
                )().format(
                    columns=", ".join(constraint.columns),
                )
            )
        return sql
