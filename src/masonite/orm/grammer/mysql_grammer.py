import pymysql.cursors
from masonite.testing import TestCase
from .BaseGrammer import BaseGrammer


class MySQLGrammer(BaseGrammer):

    """The keys in this dictionary is how the ORM will reference these aggregates

    The values on the right are the matching functions for the grammer
    
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
    table = "users"

    def __init__(
        self,
        columns="*",
        table="users",
        wheres=(),
        limit=False,
        updates={},
        aggregates=(),
        order_by=(),
        group_by=(),
        creates=(),
    ):
        self._columns = columns
        self.table = table
        self._wheres = wheres
        self._limit = limit
        self._updates = updates
        self._aggregates = aggregates
        self._order_by = order_by
        self._group_by = group_by
        self._creates = creates

        self._bindings = ()

        self._sql = ""

        self._sql_qmark = ""

    def select_format(self):
        return "SELECT {columns} FROM {table} {wheres} {group_by}{order_by}{limit}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def aggregate_string(self):
        return "{aggregate_function}({column}) AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}, "

    def create_start(self):
        return "CREATE TABLE {table} "

    def create_column_length(self):
        return "({length})"
    
    def table_string(self):
        return "`{table}`"

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "`{column}`{seperator}"

    def value_string(self):
        return "'{value}'{seperator}"

    def limit_string(self):
        return "LIMIT {limit}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"
