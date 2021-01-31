from .BaseGrammar import BaseGrammar
import re


class PostgresGrammar(BaseGrammar):
    """Postgres grammar class."""

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

    column_strings = {
        "select": '{table}."{column}"{alias}{separator}',
        "select_all": "{table}.*{separator}",
        "insert": '"{column}"{separator}',
        "update": '"{column}"{separator}',
        "delete": '{table}."{column}"{separator}',
    }

    def select_format(self):
        return "SELECT {columns} FROM {table} {joins} {wheres} {group_by} {order_by} {limit} {offset} {having}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values}) RETURNING *"

    def bulk_insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES {values} RETURNING *"

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def aggregate_string_with_alias(self):
        return "{aggregate_function}({column}) AS {alias}"

    def aggregate_string_without_alias(self):
        return "{aggregate_function}({column})"

    def subquery_string(self):
        return "({query})"

    def raw_query_string(self):
        return "{keyword} {query}"

    def where_group_string(self):
        return "{keyword} {value}"

    def between_string(self):
        return "{keyword} {column} BETWEEN {low} AND {high}"

    def not_between_string(self):
        return "{keyword} {column} NOT BETWEEN {low} AND {high}"

    def where_exists_string(self):
        return "{keyword} EXISTS {value}"

    def where_like_string(self):
        return "{keyword} {column} ILIKE {value}"

    def where_not_like_string(self):
        return "{keyword} {column} NOT ILIKE {value}"

    def subquery_alias_string(self):
        return "AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'{separator}"

    def column_value_string(self):
        return "{column} = {value}{separator}"

    def increment_string(self):
        return "{column} = {column} + '{value}'"

    def decrement_string(self):
        return "{column} = {column} - '{value}'"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}, "

    def column_exists_string(self):
        return "SELECT column_name FROM information_schema.columns WHERE table_name='{clean_table}' and column_name={value}"

    def table_exists_string(self):
        return (
            "SELECT * from information_schema.tables where table_name='{clean_table}'"
        )

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

    def to_sql(self):
        """Cleans up the SQL string and returns the SQL

        Returns:
            string
        """

        if self.queries and (not self._columns and not self._creates):
            sql = ""
            for query in self.queries:
                query += "; "
                sql += re.sub(" +", " ", query)
            return sql.rstrip(" ")
        else:
            sql = re.sub(" +", " ", self._sql.strip().replace(",)", ")"))
            for query in self.queries:
                sql += "; "
                sql += re.sub(" +", " ", query.strip())

            return sql

    def table_string(self):
        return '"{table}"'

    def order_by_format(self):
        return "{column} {direction}"

    def order_by_string(self):
        return "ORDER BY {order_columns}"

    def column_string(self):
        return '"{column}"{separator}'

    def value_string(self):
        return "'{value}'{separator}"

    def join_string(self):
        return "{keyword} {foreign_table} ON {column1} {equality} {column2}"

    def limit_string(self, offset=False):
        return "LIMIT {limit}"

    def offset_string(self):
        return "OFFSET {offset}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def or_where_string(self):
        return "OR"

    def where_in_string(self):
        return "WHERE IN ({values})"

    def value_equal_string(self):
        return "{keyword} {value1} = {value2}"

    def where_string(self):
        return " {keyword} {column} {equality} {value}"

    def having_string(self):
        return "HAVING {column}"

    def having_equality_string(self):
        return "HAVING {column} {equality} {value}"

    def where_null_string(self):
        return "{keyword} {column} IS NULL"

    def where_not_null_string(self):
        return " {keyword} {column} IS NOT NULL"
