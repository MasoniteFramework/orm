from .BaseGrammar import BaseGrammar
from ..Blueprint import Column
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

    null_map = {
        False: "NOT NULL",
        True: "NULL"
    }

    """
    @override
    """    
    def _compile_alter(self):
        """Compiles a query for altering table schemas.

        Returns:
            self
        """
        # Need to make an alter statement for each column:
        sql = []

        # Add columns to the table
        # for column in self.get_columns_to_add():

        #     sql.append(self.alter_format().format(
        #         table=self._compile_table(self.table),
        #         columns=self._compile_alter_column(column),
        #         constraints=self._compile_alter_constraints(),
        #         foreign_keys=self._compile_alter_foreign_keys(),
        #     ).strip().rstrip(','))
        
        # Need to drop columns now. So need to get the existing columns on the table and remove any columns we need to drop
        modifying_columns = self.get_columns_to_modify()
        sql += self.complex_alter_format().format(
            table=self._compile_table(self.table),
            clean_table=self.table,
            column_names=', '.join(self.columnize_names(modifying_columns)),
            columns=', '.join(self.columnize(self.with_columns_to_add(modifying_columns))),
            constraints=',' + self._compile_alter_constraints() if self._constraints else "",
            foreign_keys=',' + self._compile_alter_foreign_keys() if self._foreign_keys else "",
        ).strip().rstrip(',').split(';')

        self._sql = sql
        

        return self

    def with_columns_to_add(self, columns):
        columns += self.get_columns_to_add()
        return columns

    
    
    def columnize(self, columns):
        sql = []
        print('columnize')
        for column in columns:
            print(column.length)
            if column.length:
                length = self.create_column_length(column.column_type).format(length=column.length)
            else:
                length = ""
            sql.append(self.columnize_string().format(
                name=self._compile_column(column.column_name),
                data_type=self.type_map.get(column.column_type, ""),
                length=length,
                nullable=self.null_map.get(column.is_null) or ""
            ).strip())
        
        return sql
    
    def columnize_names(self, columns):
        sql = []
        for column in columns:
            sql.append(column.column_name)
        
        return sql
    
    def get_columns_to_add(self):
        columns = ()
        for column in self._creates:
            if column._action in ("add",):
                columns += (column,)

        return columns

    def remove_columns_by_name(self, name, columns):
        return_columns = ()
        for column in columns:
            if not column.column_name in name:
                return_columns += (column,)

        return return_columns

    def get_column_names_from_action(self, action=()):
        names = ()
        for column in self._creates:
            if column._action in action:
                names += (column.column_name,)

        return names

    def get_columns_from_action(self, action=()):
        columns = ()
        for column in self._creates:
            if column._action in action:
                columns += (column,)

        return columns
    
    def get_columns_to_modify(self):
        columns = ()
        columns += self.get_table_columns()
        columns = self.remove_columns_by_name(self.get_column_names_from_action(["drop"]), columns)
        columns = self.remove_columns_by_name(self.get_column_names_from_action(["modify"]), columns)
        columns += self.get_columns_from_action(["modify"])

        return columns

    def _compile_alter_column(self, column):
        """Compiles the columns for alter statements.

        Returns:
            self
        """
        sql = ""
        nullable = ""
        if column.is_null and column._action in ("add", "modify"):
            nullable = " NULL"
        elif not column.is_null:
            nullable = " NOT NULL"

        print('nullable', nullable)
        sql += getattr(self, "{}_column_string".format(column._action))().format(
            column=self._compile_column(column.column_name),
            old_column=self._compile_column(column.old_column),
            data_type=self.type_map.get(column.column_type, ""),
            length=self.create_column_length(column.column_type).format(
                length=column.length
            )
            if column.length
            else "",
            nullable=nullable,
            separator=",",
            after=self.after_column_string().format(
                after=self._compile_column(column.after_column)
            )
            if column.after_column
            else "",
        )

        # Fix any inconsistencies
        sql = sql.replace(" ,", ",")

        return sql

    def process_table_columns_string(self):
        return "PRAGMA table_info(users);"
    
    def get_table_columns(self):
        columns = (Column("integer", "age", nullable=False), Column("string", "name", nullable=False))
        return columns

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
    
    def columnize_string(self):
        return "{name} {data_type}{length} {nullable}"

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

    def complex_alter_format(self):
        return "CREATE TEMPORARY TABLE __temp__{clean_table} as select {column_names} from {table};DROP TABLE {table};CREATE TABLE {table} ({columns}{constraints}{foreign_keys});INSERT INTO {table} ({column_names}) select {column_names} from __temp__{clean_table}"

    def create_column_length(self, column_type):
        if column_type in self.types_without_lengths:
            return ""
        return "({length})"

    def unique_constraint_string(self):
        return "CONSTRAINT {index_name} UNIQUE ({clean_column}){separator}"

    def create_unique_column_string(self):
        return "CONSTRAINT {index_name} UNIQUE({clean_column}){separator}"

    def primary_key_string(self):
        return "{table}_primary"

    def index_constraint_string(self):
        return (
            """CREATE INDEX {clean_table}_{clean_column}_index ON {table}({column})"""
        )
    
    def only_foreign_keys(self):
        return self._foreign_keys and not (
            self._creates and
            self._constraints
        )

    def to_sql(self):
        """Cleans up the SQL string and returns the SQL

        Returns:
            string
        """
        return self._sql

    def fulltext_constraint_string(self):
        return "CREATE INDEX {clean_table}_{clean_column}_index ON {table}({column})"

    def primary_constraint_string(self):
        return "PRIMARY KEY ({column}){separator}"

    def foreign_key_string(self):
        return "CONSTRAINT {index_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}){separator}"

    def alter_foreign_key_string(self):
        return "CONSTRAINT {index_name} FOREIGN KEY ({column}) REFERENCES {foreign_table}({foreign_column}) {action}{separator}"

    def table_string(self):
        return '"{table}"'

    def column_string(self):
        return '"{column}"{separator}'

    def value_string(self):
        return "'{value}'{separator}"

    def value_equal_string(self):
        return "{keyword} {value1} = {value2}"

    def after_column_string(self):
        return ""

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
