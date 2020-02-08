class MSSQLGrammer:

    _columns = '*'

    _sql = ''

    table = 'users'

    _wheres = ()

    _limit = False

    def _compile_select(self):
        self._sql = 'SELECT {limit} {columns} FROM {table} {wheres}'.format(
            columns=self._compile_columns(seperator=', '),
            table=self._compile_from(),
            wheres=self._compile_wheres(),
            limit=self._compile_limit()).strip().replace('  ', ' ')

        return self

    def _compile_from(self):
        return "[{table}]".format(table=self.table)

    def _compile_limit(self):
        if not self._limit:
            return ''

        return "TOP {limit}".format(limit=self._limit)

    def select(self, *args):
        self._columns = list(args)
        return self

    def where(self, column, value):
        self._wheres += ((column, '=', value),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

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
            sql += "{keyword} {column} {equality} '{value}'".format(
                keyword=keyword, column=column, equality=equality, value=value)
            loop_count += 1
        return sql

    def to_sql(self):
        print(self._sql)
        return self._sql

    def _compile_columns(self, seperator=''):
        sql = ''
        if self._columns == '*':
            return self._columns

        for column in self._columns:
            sql += self._compile_column(column, seperator=seperator)

        return sql[:-2]

    def _compile_column(self, column, seperator=''):
        return "[{column}]{seperator}".format(column=column, seperator=seperator)

