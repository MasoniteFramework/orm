import pymysql.cursors
from masonite.testing import TestCase

class MySQLGrammer:

    _columns = '*'

    _sql = ''

    table = 'users'

    _wheres = ()

    _limit = False

    def __init__(self, columns='*', table='users', wheres=(), limit=False):
        self._columns = columns 
        self.table = table 
        self._wheres = wheres 
        self._limit = limit 

    def _compile_select(self):
        self._sql = 'SELECT {columns} FROM {table} {wheres} {limit}'.format(
            columns=self._compile_columns(seperator=', '), 
            table=self._compile_from(), 
            wheres=self._compile_wheres(),
            limit=self._compile_limit()).strip()
            
        return self

    def _compile_from(self):
        return "`{table}`".format(table=self.table)

    def _compile_limit(self):
        if not self._limit:
            return ''

        return "LIMIT {limit}".format(limit=self._limit)


    def _compile_wheres(self):
        sql = ''
        loop_count = 0
        for where in self._wheres:
            if loop_count == 0:
                keyword = "WHERE"
            else:
                keyword = " AND"

            column, equality, value = where
            column = self._compile_column(column)
            sql += "{keyword} {column} {equality} '{value}'".format(keyword=keyword, column=column, equality=equality, value=value)
            loop_count += 1
        return sql

    def select(self, *args):
        self._columns = list(args)
        return self

    def where(self, column, value):
        self._wheres += ((column, '=', value),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

    def to_sql(self):
        print('calling to sql', self._sql)
        return self._sql

    def _compile_columns(self, seperator=''):
        sql = ''
        if self._columns == '*':
            return self._columns
        
        for column in self._columns:
            sql += self._compile_column(column, seperator=seperator)
        
        return sql[:-2]

    def _compile_column(self, column, seperator=''):
        return "`{column}`{seperator}".format(column=column, seperator=seperator)






class User:

    _columns = '*'

    table = 'users'

    _wheres = ()

    _limit = False

    _grammer = MySQLGrammer

    def select(self, *args):
        self._columns = list(args)
        return self

    def where(self, column, value):
        self._wheres += ((column, '=', value),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

    def first(self):
        # Connect to the database
        connection = pymysql.connect(host='localhost',
                                    user='root',
                                    password='',
                                    db='gbaleague',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        query = self._grammer(
            columns=self._columns,
            table=self.table,
            wheres=self._wheres,
            limit=self._limit,
        )._compile_select().to_sql()

        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = query
                cursor.execute(sql)
                result = cursor.fetchone()
                print(result)
        finally:
            connection.close()

User().select('*').where('id', '1').first()