from .BaseGrammar import BaseGrammar
import re


class SQLiteGrammar(BaseGrammar):
    """SQLite grammar class."""

    types_without_lengths = []

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

    options = {
        "create_constraints_as_separate_queries": True,  # Whether constraints should run as separate queries or part of the create table semantics
        "alter_constraints_as_separate_queries": True,  # Whether constraints should run as separate queries or part of the alter table semantics
        "second_query_constraints": (
            "index",
            "fulltext",
        ),  # constraint types that should run as separate queries
        "can_compile_multiple_index": False,  # INDEX("column1", "column2")
    }

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT CURRENT_TIMESTAMP",
        "null": " DEFAULT NULL",
    }

    def default_string(self):
        return " DEFAULT {default} "

    def raw_query_string(self):
        return "{keyword} {query}"

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
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{clean_table}'"
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

    def column_string(self):
        return '"{column}"{separator}'

    def value_string(self):
        return "'{value}'{separator}"

    def value_equal_string(self):
        return "{keyword} {value1} = {value2}"

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
