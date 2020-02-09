class Column:

    def __init__(self, column_type, column_name, length=None, nullable=False):
        self.column_type = column_type
        self.column_name = column_name
        self.length = length
        self.is_null = nullable

    def nullable(self):
        self.is_null = True
        return self

    def not_nullable(self):
        self.is_null = False
        return self

class Blueprint:
    def __init__(self, grammar, table=""):
        self.grammar = grammar
        self.table = table
        self._sql = ""
        self._columns = ()
        self._last_column = None

    def string(self, column, length=255, nullable=False):
        self._last_column = self.new_column('string', column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def new_column(self, column_type, column, length=255, nullable=False):
        return Column(column_type, column, length, nullable)

    def integer(self, column, length=11, nullable=False):
        self._last_column = self.new_column("integer", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def _compile_create(self):
        return self.grammar(creates=self._columns, table=self.table)._compile_create()

    def increments(self, column, nullable=False):
        self._last_column = self.new_column("increments", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def big_increments(self):
        pass

    def binary(self, column, nullable=False):
        self._last_column = self.new_column("binary", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def boolean(self, column, nullable=False):
        self._last_column = self.new_column("boolean", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def char(self, column, length=1, nullable=False):
        self._last_column = self.new_column("char", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def date(self, column, nullable=False):
        self._last_column = self.new_column("date", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def datetime(self, column, nullable=False):
        self._last_column = self.new_column("datetime", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def decimal(self, column, length=17, precision=6, nullable=False):
        self._last_column = self.new_column("decimal", column, "{}, {}".format(length, precision), nullable)
        self._columns += (self._last_column,)
        return self

    def double(self):
        pass

    def enum(self, column, options=[], nullable=False):
        new_options = ""
        for option in options:
            new_options += "'{}',".format(option)
        new_options = new_options.rstrip(",")
        self._last_column = self.new_column("enum", column, new_options, nullable)
        self._columns += (self._last_column,)
        return self

    def text(self, column, length=None, nullable=False):
        self._last_column = self.new_column("text", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def unsigned(self, column, length=None, nullable=False):
        self._last_column = self.new_column("unsigned", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def unsigned_integer(self):
        pass

    def to_sql(self):
        return (
            self.grammar(creates=self._columns, table=self.table)
            ._compile_create()
            .to_sql()
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def nullable(self):
        self._last_column.nullable()
        return self
