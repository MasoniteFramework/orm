from .BaseGrammar import BaseGrammar


class MSSQLGrammar(BaseGrammar):
    """Microsoft SQL Server grammar class.
    """

    aggregate_options = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "AVG": "AVG",
        "COUNT": "COUNT",
        "AVG": "AVG",
    }

    join_keywords = {
        "inner": "INNER JOIN",
        "outer": "OUTER JOIN",
        "left": "LEFT JOIN",
        "right": "RIGHT JOIN",
        "left_inner": "LEFT INNER JOIN",
        "right_inner": "RIGHT INNER JOIN",
    }

    def select_format(self):
        return "SELECT {limit} {columns} FROM {table} {joins} {wheres} {group_by}{order_by} {offset} {having}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}, "

    def create_start(self):
        return "CREATE TABLE {table} "

    def having_string(self):
        return "HAVING {column}"

    def where_exists_string(self):
        return "{keyword} EXISTS {value}"

    def having_equality_string(self):
        return "HAVING {column} {equality} {value}"

    def aggregate_string_without_alias(self):
        return "{aggregate_function}({column})"

    def create_column_length(self):
        return "({length})"

    def limit_string(self, offset=False):
        if offset:
            return ""
        return "TOP {limit}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def join_string(self):
        return "{keyword} {foreign_table} ON {local_table}.{column1} {equality} {foreign_table}.{column2}"

    def aggregate_string(self):
        return "{aggregate_function}({column}) AS {alias}"

    def subquery_string(self):
        return "({query})"

    def where_group_string(self):
        return "{keyword} {value}"

    def or_where_string(self):
        return "OR"

    def raw_query_string(self):
        return "{keyword} {query}"

    def where_in_string(self):
        return "WHERE IN ({values})"

    def where_null_string(self):
        return "{keyword} {column} IS NULL"

    def between_string(self):
        return "{keyword} {column} BETWEEN {low} AND {high}"

    def not_between_string(self):
        return "{keyword} {column} NOT BETWEEN {low} AND {high}"

    def where_not_null_string(self):
        return "{keyword} {column} IS NOT NULL"

    def where_string(self):
        return " {keyword} {column} {equality} {value}"

    def offset_string(self):
        return "OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"

    def aggregate_string_with_alias(self):
        return "{aggregate_function}({column}) AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'"

    def table_string(self):
        return "[{prefix}{table}]"

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "[{column}]{separator}"

    def value_string(self):
        return "'{value}'{separator}"
