from .BaseGrammer import BaseGrammer


class MSSQLGrammer(BaseGrammer):

    aggregate_options = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "AVG": "AVG",
        "COUNT": "COUNT",
        "AVG": "AVG",
    }

    def select_format(self):
        return "SELECT {limit} {columns} FROM {table} {wheres} {group_by}{order_by}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def limit_string(self):
        return "TOP {limit}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def aggregate_string(self):
        return "{aggregate_function}({column}) AS {alias}"

    def key_value_string(self):
        return "[{column}] = '{value}'"

    def table_string(self):
        return "[{table}]"

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "[{column}]{seperator}"

    def value_string(self):
        return "'{value}'{seperator}"
