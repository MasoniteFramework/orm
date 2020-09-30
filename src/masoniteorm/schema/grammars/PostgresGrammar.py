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

    types_without_lengths = ["integer"]

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INTEGER",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "SERIAL UNIQUE",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "SERIAL UNIQUE",
        "binary": "LONGBLOB",
        "boolean": "BOOLEAN",
        "decimal": "DECIMAL",
        "double": "DOUBLE",
        "enum": "VARCHAR(255) CHECK ",
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
        "datetime": "TIMESTAMP",
        "tiny_increments": "TINYINT AUTO_INCREMENT",
        "unsigned": "INT",
        "unsigned_integer": "INT",
    }

    on_delete_mapping = {
        "cascade": "ON DELETE CASCADE",
        "null": "ON DELETE SET NULL",
        None: "",
    }

    on_update_mapping = {
        "cascade": "ON UPDATE CASCADE",
        "null": "ON UPDATE SET NULL",
        None: "",
    }

    column_strings = {
        "select": '"{table}"."{column}"{separator}',
        "insert": '"{column}"{separator}',
        "update": '"{column}"{separator}',
        "delete": '"{table}"."{column}"{separator}',
    }

    options = {
        "create_constraints_as_separate_queries": True,
        "alter_constraints_as_separate_queries": True,
        "second_query_constraints": ("index", "fulltext"),
        "can_compile_multiple_index": False,  # INDEX("column1", "column2")
    }

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT NOW()",
        "null": " DEFAULT NULL",
    }

    premapped_nulls = {
        "null": " NULL ",
        "not_null": " NOT NULL ",
    }

    def select_format(self):
        return "SELECT {columns} FROM {table} {joins} {wheres} {group_by}{order_by} {limit} {offset} {having}"

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

    def not_between_string(self):
        return "{keyword} {column} NOT BETWEEN {low} AND {high}"

    def where_exists_string(self):
        return "{keyword} EXISTS {value}"

    def subquery_alias_string(self):
        return "AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'{separator}"

    def increment_string(self):
        return "{column} = {column} + '{value}'"

    def decrement_string(self):
        return "{column} = {column} - '{value}'"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}{default_value}, "

    def _type_enum(self, column, length_string, default=None):
        return f""""{column.column_name}" VARCHAR(255) CHECK ("{column.column_name}" in {length_string})"""

    def create_column_string_with_default(self):
        return "{column} {data_type}{length} DEFAULT {default_value}, "

    def column_exists_string(self):
        return "SELECT column_name FROM information_schema.columns WHERE table_name='{clean_table}' and column_name={value}"

    def table_exists_string(self):
        return (
            "SELECT * from information_schema.tables where table_name='{clean_table}'"
        )

    def add_column_string(self):
        return "ADD {column} {data_type}{length}{nullable} {after}, "

    def drop_column_string(self):
        return "DROP COLUMN {column}, "

    def modify_column_string(self):
        return "MODIFY {column} {data_type}{length}{nullable} {after}, "

    def rename_column_string(self):
        return "RENAME COLUMN {old_column} TO {column} {data_type}{length}{nullable}, "

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints}{foreign_keys})"

    def alter_format(self):
        return "ALTER TABLE {table} {columns}{constraints}{foreign_keys}"

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

    def unique_constraint_string(self):
        return "CONSTRAINT {index_name} UNIQUE ({clean_column}){separator}"

    def create_unique_column_string(self):
        return "ADD CONSTRAINT {index_name} UNIQUE({column}){separator}"

    def primary_key_string(self):
        return "{table}_primary"

    def index_constraint_string(self):
        return (
            """CREATE INDEX {clean_table}_{clean_column}_index ON {table}({column})"""
        )

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

    def fulltext_constraint_string(self):
        return "CREATE INDEX {clean_table}_{clean_column}_index ON {table}({column})"

    def primary_constraint_string(self):
        return "PRIMARY KEY ({column}){separator}"

    def foreign_key_string(self):
        return "CONSTRAINT {index_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}){separator}"

    def alter_foreign_key_string(self):
        return "ADD CONSTRAINT {index_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}) {action}{separator}"

    def table_string(self):
        return '"{table}"'

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return '"{column}"{separator}'

    def default_string(self):
        return " DEFAULT {default} "

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

    def after_column_string(self):
        return "AFTER {after}"

    def drop_table_string(self):
        return "DROP TABLE {table}"

    def drop_table_if_exists_string(self):
        return "DROP TABLE IF EXISTS {table}"

    def truncate_table_string(self):
        return "TRUNCATE {table}"

    def rename_table_string(self):
        return "ALTER TABLE {current_table_name} RENAME TO {new_table_name}"

    def drop_index_column_string(self):
        return "DROP INDEX {column}{separator} "

    def drop_unique_column_string(self):
        return "DROP CONSTRAINT {clean_column}{separator} "

    def drop_foreign_column_string(self):
        return "DROP CONSTRAINT {clean_column}{separator} "

    def drop_primary_column_string(self):
        return "DROP CONSTRAINT {clean_table}_primary{separator} "
