from .BaseGrammar import BaseGrammar


class MySQLGrammar(BaseGrammar):
    """MySQL grammar class."""

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INT",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "BIGINT AUTO_INCREMENT",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY",
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
        "unsigned_integer": "INT UNSIGNED",
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
        "create_constraints_as_separate_queries": False,  # Whether constraints should run as separate queries or part of the create table semantics
        "alter_constraints_as_separate_queries": False,  # Whether constraints should run as separate queries or part of the alter table semantics
        "second_query_constraints": (),  # constraint types that should run as separate queries
        "can_compile_multiple_index": True,  # INDEX("column1", "column2")
    }

    """Column strings are formats for how columns and key values should be formatted
    on specific queries. These can be different depending on the type of query.

    For example for Postgres, You can specify columns as "users"."name":

        SELECT "users"."name" from "users"

    But on updates we can only specify the column name and cannot have the table prefixed:

        UPDATE "users" SET "name" = "value"

    This dictionary allows you to modify the format depending on the type
    of query we are generating. For most databases these will be the same
    but this allows you to modify formats depending on the database.
    """

    premapped_defaults = {
        "current": " DEFAULT CURRENT_TIMESTAMP",
        "now": " DEFAULT NOW()",
        "null": " DEFAULT NULL",
    }

    premapped_nulls = {
        "null": " NULL ",
        "not_null": " NOT NULL ",
    }

    def key_value_string(self):
        return "{column} = '{value}'{separator}"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}{default_value}, "

    def default_string(self):
        return " DEFAULT {default} "

    def column_exists_string(self):
        return "SHOW COLUMNS FROM {table} LIKE {value}"

    def table_exists_string(self):
        return "SELECT * from information_schema.tables where table_name='{clean_table}' AND table_schema = '{database}'"

    def add_column_string(self):
        return "ADD {column} {data_type}{length}{nullable} {after}{separator} "

    def drop_column_string(self):
        return "DROP COLUMN {column}, "

    def modify_column_string(self):
        return "MODIFY {column} {data_type}{length}{nullable} {after}, "

    def rename_column_string(self):
        return "CHANGE COLUMN {old_column} {column} {data_type}{length}{nullable}, "

    def create_format(self):
        return "CREATE TABLE {table} ({columns}{constraints}{foreign_keys})"

    def alter_format(self):
        return "ALTER TABLE {table} {columns}{constraints}{foreign_keys}"

    def create_column_length(self, column_type):
        return "({length})"

    def unique_constraint_string(self):
        return "CONSTRAINT {index_name} UNIQUE ({clean_column}){separator}"

    def index_constraint_string(self):
        return "INDEX ({column}){separator}"

    def primary_key_string(self):
        return "{table}_primary"

    def fulltext_constraint_string(self):
        return "FULLTEXT ({column}){separator}"

    def primary_constraint_string(self):
        return "PRIMARY KEY ({column}){separator}"

    def foreign_key_string(self):
        return "CONSTRAINT {index_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}){separator}"

    def alter_foreign_key_string(self):
        return "ADD CONSTRAINT {index_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}) {action}{separator}"

    def table_string(self):
        return "`{table}`"

    def column_string(self):
        return "`{column}`{separator}"

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
        return "TRUNCATE TABLE {table}"

    def rename_table_string(self):
        return "RENAME TABLE {current_table_name} TO {new_table_name}"

    def create_unique_column_string(self):
        return "ADD CONSTRAINT {index_name} UNIQUE({column}){separator}"

    def drop_index_column_string(self):
        return "DROP INDEX {column} "

    def drop_unique_column_string(self):
        return "DROP INDEX {column} "

    def drop_foreign_column_string(self):
        return "DROP FOREIGN KEY {column} "

    def drop_primary_column_string(self):
        return "DROP PRIMARY KEY"
