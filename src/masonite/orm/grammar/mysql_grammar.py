import pymysql.cursors
from masonite.testing import TestCase
from .BaseGrammar import BaseGrammar


class MySQLGrammar(BaseGrammar):

    """The keys in this dictionary is how the ORM will reference these aggregates

    The values on the right are the matching functions for the grammar

    Returns:
        [type] -- [description]
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

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INT",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "BIGINT",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "INT AUTO_INCREMENT PRIMARY KEY",
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

    timestamp_mapping = {"current": "CURRENT_TIMESTAMP", "now": "NOW()"}

    def select_format(self):
        return "SELECT {columns} FROM {table} {joins} {wheres} {group_by}{order_by}{limit} {offset} {having}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

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

    def where_exists_string(self):
        return "{keyword} EXISTS {value}"

    def subquery_alias_string(self):
        return "AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'"

    def increment_string(self):
        return "{column} = {column} + '{value}'"

    def decrement_string(self):
        return "{column} = {column} - '{value}'"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}, "

    def create_column_string_with_default(self):
        return "{column} {data_type}{length} DEFAULT {default_value}, "

    def column_exists_string(self):
        return "SHOW COLUMNS FROM {table} LIKE {value}"

    def add_column_string(self):
        return "ADD {column} {data_type}{length}{nullable} {after}, "

    def drop_column_string(self):
        return "DROP COLUMN {column}, "

    def modify_column_string(self):
        return "MODIFY {column} {data_type}{length}{nullable} {after}, "

    def rename_column_string(self):
        return "CHANGE COLUMN old_name {column} {data_type}{length}{nullable}, "

    def create_start(self):
        return "CREATE TABLE {table} "

    def alter_start(self):
        return "ALTER TABLE {table} "

    def create_column_length(self):
        return "({length})"

    def unique_constraint_string(self):
        return "CONSTRAINT {clean_column}_unique UNIQUE ({clean_column})"

    def table_string(self):
        return "`{table}`"

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "`{column}`{seperator}"

    def value_string(self):
        return "'{value}'{seperator}"

    def join_string(self):
        return "{keyword} {foreign_table} ON {local_table}.{column1} {equality} {foreign_table}.{column2}"

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

    def where_string(self):
        return " {keyword} {column} {equality} {value}"

    def having_string(self):
        return "HAVING {column}"

    def having_equality_string(self):
        return "HAVING {column} {equality} {value}"

    def where_null_string(self):
        return "{keyword} {column} IS NULL"

    def where_not_null_string(self):
        return "{keyword} {column} IS NOT NULL"

    def after_column_string(self):
        return "AFTER {after}"

    def drop_table_string(self):
        return "DROP TABLE {table}"

    def drop_table_if_exists_string(self):
        return "DROP TABLE IF EXISTS {table}"
