"""This module homes the GrammarExample class.

This class can be used for creating new grammar classes
"""


class GrammarExample:

    aggregate_options = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "AVG": "AVG",
        "COUNT": "COUNT",
        "AVG": "AVG",
    }

    def select_format(self):
        """This method will dictate how select statements are structured.
        This makes moving the position of clauses a cinch. Especially in scenarios
        like MSSQL where the limit clause is before the selecting of column.

        This should return a string using the magic keywords below.

        Magic keywords include:

        columns - Will be a seperated list of column values.
            This could be `column1`, `column2` for mysql or
            [column1], [column2] for mssql. This is dependant
            on the grammar class implementation.

        table - The table name.

        wheres - Will be a seperated list of where clauses. This is dependant
            on the grammar class implementation.

        group_by - A group by clause.

        order_by - An order by clause.

        limit - A limit clause.

        Returns:
            [type] -- [description]
        """
        return "SELECT {columns} FROM {table} {wheres} {group_by}{order_by}{limit}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

    def where_in_string(self):
        return "WHERE IN ({values})"

    def where_string(self):
        return " {keyword} {column} {equality} {value}"

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def column_exists_string(self):
        return "SHOW COLUMNS FROM {table} LIKE {value}"

    def unique_constraint_string(self):
        property()
        return "CONSTRAINT {clean_column}_unique UNIQUE ({clean_column})"

    def limit_string(self):
        return "LIMIT {limit}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def aggregate_string_with_alias(self):
        return "{aggregate_function}({column}) AS {alias}"

    def aggregate_string_without_alias(self):
        return "{aggregate_function}({column})"

    def key_value_string(self):
        return "{column} = '{value}'"

    def table_string(self):
        return "`{table}`"

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "`{column}`{separator}"

    def value_string(self):
        return "'{value}'{separator}"

    def after_column_string(self):
        return " AFTER `{after}`"
