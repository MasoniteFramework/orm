"""This module homes the GrammerExample class.

This class can be used for creating new grammer classes
"""


class GrammerExample:

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
            on the grammer class implementation.

        table - The table name.

        wheres - Will be a seperated list of where clauses. This is dependant
            on the grammer class implementation.

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

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def limit_string(self):
        return "LIMIT {limit}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def aggregate_string(self):
        return "{aggregate_function}({column}) AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'"

    def table_string(self):
        return "`{table}`"

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "`{column}`{seperator}"

    def value_string(self):
        return "'{value}'{seperator}"
