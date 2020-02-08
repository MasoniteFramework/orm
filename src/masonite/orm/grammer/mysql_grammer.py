import pymysql.cursors
from masonite.testing import TestCase

class MySQLGrammer:

    _columns = '*'

    _sql = ''

    _updates = {}

    table = 'users'

    _wheres = ()

    _limit = False

    def __init__(self, columns='*', table='users', wheres=(), limit=False, updates={}):
        self._columns = columns 
        self.table = table 
        self._wheres = wheres 
        self._limit = limit 
        self._updates = updates 

    def _compile_select(self):
        self._sql = 'SELECT {columns} FROM {table} {wheres} {limit}'.format(
            columns=self._compile_columns(seperator=', '), 
            table=self._compile_from(), 
            wheres=self._compile_wheres(),
            limit=self._compile_limit()).strip()

        return self

    def _compile_update(self):
        self._sql = 'UPDATE {table} SET {key_equals} {wheres}'.format(
            key_equals=self._compile_key_value_equals(), 
            table=self._compile_from(),
            wheres=self._compile_wheres())
            
        return self

    def _compile_insert(self):
        self._sql = 'INSERT INTO {table} ({columns}) VALUES ({values})'.format(
            key_equals=self._compile_key_value_equals(), 
            table=self._compile_from(),
            columns=self._compile_columns(seperator=', '), 
            values=self._compile_values(seperator=', '), 
            )
            
        return self

    def _compile_delete(self):
        self._sql = 'DELETE FROM {table} {wheres}'.format(
            key_equals=self._compile_key_value_equals(), 
            table=self._compile_from(),
            wheres=self._compile_wheres()
        )
            
        return self

    def _compile_key_value_equals(self):
        sql = ''
        for column, value in self._updates.items():
            sql += "{column} = '{value}'".format(
                column = self._compile_column(column),
                value=value)

        return sql

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

    def create(self, creates):
        self._columns = creates
        return self

    def delete(self, column, value):
        self.where(column, value)
        return self

    def where(self, column, value):
        self._wheres += ((column, '=', value),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

    def update(self, updates):
        self._updates = updates
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

    def _compile_values(self, seperator=''):
        sql = ''
        if self._columns == '*':
            return self._columns
        
        for column, value in self._columns.items():
            sql += self._compile_value(value, seperator=seperator)
        
        return sql[:-2]

    def _compile_column(self, column, seperator=''):
        return "`{column}`{seperator}".format(column=column, seperator=seperator)

    def _compile_value(self, value, seperator=''):
        return "'{value}'{seperator}".format(value=value, seperator=seperator)




