class Platform:
    foreign_key_actions = {
        "set null": "SET NULL",
        "cascade": "CASCADE",
        "restrict": "RESTRICT",
        "no action": "NO ACTION",
        "default": "SET DEFAULT",
    }

    signed = {"signed": "SIGNED", "unsigned": "UNSIGNED"}

    def columnize(self, columns):
        raise NotImplementedError

    def columnize_string(self):
        raise NotImplementedError

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

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
                    foreign_column=self.wrap_column(
                        foreign_key.foreign_column
                    ),
                    cascade=cascade,
                )
            )
        return sql

    def constraintize(self, constraints):
        sql = []
        for name, constraint in constraints.items():
            sql.append(
                getattr(
                    self, f"get_{constraint.constraint_type}_constraint_string"
                )().format(columns=", ".join(constraint.columns))
            )
        return sql

    def wrap_table(self, table_name):
        return self.get_table_string().format(table=table_name)

    def wrap_column(self, column_name):
        return self.get_column_string().format(column=column_name)
