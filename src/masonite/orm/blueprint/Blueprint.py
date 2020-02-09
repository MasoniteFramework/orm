class Blueprint:
    def __init__(self, grammer, table=""):
        self.grammer = grammer
        self.table = table
        self._sql = ""
        self._columns = ()

    def string(self, column, length=255, nullable=True):
        self._columns += (("string", column, length, nullable,),)
        return self

    def integer(self, column, length=11, nullable=True):
        self._columns += (("integer", column, length, nullable,),)
        return self

    def _compile_create(self):
        return self.grammer(creates=self._columns, table=self.table)._compile_create()

    def increments(self, column):
        self._columns += (("increments", column, None, True,),)
        return self

    def big_increments(self):
        pass

    def binary(self, column):
        self._columns += (("binary", column, None, True,),)
        return self

    def boolean(self, column):
        self._columns += (("boolean", column, None, True,),)
        return self

    def char(self, column, length=1):
        self._columns += (("char", column, length, True,),)
        return self

    def date(self, column):
        self._columns += (("date", column, None, True,),)
        return self

    def datetime(self, column):
        self._columns += (("datetime", column, None, True,),)
        return self

    def decimal(self, column, length=17, precision=6, nullable=True):
        self._columns += (
            ("decimal", column, "{}, {}".format(length, precision), nullable,),
        )
        return self

    def double(self):
        pass

    def enum(self, column, options=[], nullable=True):
        new_options = ""
        for option in options:
            new_options += "'{}',".format(option)
        new_options = new_options.rstrip(",")
        self._columns += (("enum", column, new_options, nullable,),)
        return self

    def text(self, column, length=None, nullable=True):
        self._columns += (("text", column, length, nullable,),)
        return self

    def unsigned(self, column, length=None, nullable=True):
        self._columns += (("unsigned", column, length, nullable,),)
        return self

    def unsigned_integer(self):
        pass

    def to_sql(self):
        return (
            self.grammer(creates=self._columns, table=self.table)
            ._compile_create()
            .to_sql()
        )
