class Column:
    def __init__(
        self,
        column_type,
        column_name,
        table=None,
        length=None,
        nullable=False,
        action="add",
        default=None,
    ):
        self.column_type = column_type
        self.column_name = column_name
        self.length = length
        self.table = table
        self.is_null = nullable
        self.is_constraint = False
        self.constraint_type = None
        self.after_column = None
        self.old_column = ""
        self.use_current_timestamp = False
        self.default = default
        self._action = action
        self._change = False

    def nullable(self):
        self.is_null = True
        return self

    def not_nullable(self):
        self.is_null = False
        return self

    def unique(self):
        self.is_constraint = True
        self.constraint_type = "unique"
        return self

    def rename(self, column):
        self.old_column = column
        return self

    def after(self, after_column):
        self.after_column = after_column
        return self

    def default(self, value):
        self.default = value
        return self

    def change(self):
        self._action = "modify"
        return self

    def use_current(self):
        self.default = "current"
        # self.use_current_timestamp = True
        return self


class Blueprint:
    def __init__(self, grammar, table="", action=None, default_string_length=None):
        self.grammar = grammar
        self.table = table
        self._sql = ""
        self._columns = ()
        self._last_column = None
        self._action = action
        self._default_string_length = default_string_length

    def string(self, column, length=255, nullable=False):
        self._last_column = self.new_column("string", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def new_column(
        self,
        column_type,
        column,
        length=255,
        nullable=False,
        action="add",
        default=False,
    ):
        if length == 255:
            length = self._default_string_length or length

        return Column(
            column_type,
            column,
            table=self.table,
            length=length,
            nullable=nullable,
            action=action,
            default=default,
        )

    def integer(self, column, length=11, nullable=False):
        self._last_column = self.new_column("integer", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def _compile_create(self):
        return self.grammar(creates=self._columns, table=self.table)._compile_create()

    def _compile_alter(self):
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

    def timestamp(self, column, nullable=False, now=False):
        if now:
            now = "now"

        self._last_column = self.new_column(
            "timestamp", column, None, nullable, default=now
        )
        self._columns += (self._last_column,)
        return self

    def timestamps(self):
        created_at = self.new_column(
            "timestamp", "created_at", None, nullable=False
        ).use_current()
        updated_at = self.new_column(
            "timestamp", "updated_at", None, nullable=False
        ).use_current()

        self._last_column = updated_at
        self._columns += (
            created_at,
            updated_at,
        )
        return self

    def decimal(self, column, length=17, precision=6, nullable=False):
        self._last_column = self.new_column(
            "decimal", column, "{}, {}".format(length, precision), nullable
        )
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
        if self._action == "create":
            return (
                self.grammar(creates=self._columns, table=self.table)
                ._compile_create()
                .to_sql()
            )
        else:
            return (
                self.grammar(creates=self._columns, table=self.table)
                ._compile_alter()
                .to_sql()
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def nullable(self):
        self._last_column.nullable()
        return self

    def change(self):
        self._last_column.change()
        return self

    def unique(self):
        self._last_column.unique()
        return self

    def rename(self, old_column, new_column):
        self._last_column = self.new_column(None, column, length, nullable).rename(
            old_column
        )
        self._columns += (self._last_column,)
        return self

    def after(self, old_column):
        self._last_column.after(old_column)
        return self

    def drop_column(self, *columns):
        for column in columns:
            self._last_column = self.new_column(None, column, None, None, action="drop")
            self._columns += (self._last_column,)

        return self
