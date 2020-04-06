class Column:
    """Used for creating or modifying columns.
    """

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
        """Sets this column to be nullable

        Returns:
            self
        """
        self.is_null = True
        return self

    def not_nullable(self):
        """Sets this column to be not nullable

        Returns:
            self
        """
        self.is_null = False
        return self

    def unique(self):
        """Sets this column to be unique

        Returns:
            self
        """
        self.is_constraint = True
        self.constraint_type = "unique"
        return self

    def rename(self, column):
        """Renames this column to a new name

        Arguments:
            column {string} -- The old column name

        Returns:
            self
        """
        self.old_column = column
        return self

    def after(self, after_column):
        """Sets the column that this new column should be created after.

        This is useful for setting the location of the new column in the table schema.

        Arguments:
            after_column {string} -- The column that this new column should be created after

        Returns:
            self
        """
        self.after_column = after_column
        return self

    def default(self, value):
        """Sets a default value for this column

        Arguments:
            value {string} -- A default value.

        Returns:
            self
        """
        self.default = value
        return self

    def change(self):
        """Sets the schema to create a modify sql statement.

        Returns:
            self
        """
        self._action = "modify"
        return self

    def use_current(self):
        """Sets the column to use a current timestamp.

        Used for timestamp columns.

        Returns:
            self
        """
        self.default = "current"
        return self


class Constraint:
    def __init__(self, column, constraint_type):
        self.column_name = column
        self.constraint_type = constraint_type
        if isinstance(column, (list, tuple)):
            self.index_name = "_".join(column) + "_" + constraint_type
        else:
            self.index_name = column + "_" + constraint_type


class ForeignKey:
    def __init__(self, column, current_table, foreign_table=None, foreign_column=None):
        self.column_name = column
        self.current_table = current_table
        self.foreign_table = foreign_table
        self.foreign_column = foreign_column
        self._on_delete = None
        self._on_update = None
        self.index_name = ""

    def references(self, foreign_column):
        self.foreign_column = foreign_column

    def on(self, foreign_table):
        self.foreign_table = foreign_table
        self.index_name = f"{self.current_table}_{self.column_name}_foreign"

    def on_update(self, action):
        self._on_update = action
        return self

    def on_delete(self, action):
        self._on_delete = action
        return self


class Blueprint:
    """Used for building schemas for creating, modifying or altering schema.
    """

    def __init__(self, grammar, table="", action=None, default_string_length=None):
        self.grammar = grammar
        self.table = table
        self._sql = ""
        self._columns = ()
        self._constraints = ()
        self._foreign_keys = ()
        self._last_column = None
        self._action = action
        self._default_string_length = default_string_length

    def string(self, column, length=255, nullable=False):
        """Sets a column to be the string representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            length {int} -- The length of the column. (default: {255})
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
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
        """Creates a new column and sets the appropriate attributes for creating, modifying or altering the column.

        Arguments:
            column_type {string} -- The type of the column
            column {string} -- The column name.

        Keyword Arguments:
            length {int} -- The length of the column. (default: {255})
            nullable {bool} -- Whether the column is nullable. (default: {False})
            action {string} -- The action the column should take. (default: {"add"})
            default {string|int} -- The default value for the column. (default: {False})

        Returns:
            masonite.orm.blueprint.Column - A column class.
        """
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
        """Sets a column to be the integer representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            length {int} -- The length of the column. (default: {255})
            nullable {bool} -- Whether the column is nullable (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("integer", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def _compile_create(self):
        return self.grammar(creates=self._columns, table=self.table)._compile_create()

    def _compile_alter(self):
        return self.grammar(creates=self._columns, table=self.table)._compile_create()

    def increments(self, column, nullable=False):
        """Sets a column to be the auto incrementing primary key representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("increments", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def big_increments(self):
        pass

    def binary(self, column, nullable=False):
        """Sets a column to be the binary representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("binary", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def boolean(self, column, nullable=False):
        """Sets a column to be the boolean representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("boolean", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def char(self, column, length=1, nullable=False):
        """Sets a column to be the char representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            length {int} -- The length for the column (default: {1})
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("char", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def date(self, column, nullable=False):
        """Sets a column to be the date representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("date", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def datetime(self, column, nullable=False):
        """Sets a column to be the datetime representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("datetime", column, None, nullable)
        self._columns += (self._last_column,)
        return self

    def timestamp(self, column, nullable=False, now=False):
        """Sets a column to be the timestamp representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            nullable {bool} -- Whether the column is nullable. (default: {False})
            now {bool} -- Whether the default for the column should be the current time. (default: {False})

        Returns:
            self
        """
        if now:
            now = "now"

        self._last_column = self.new_column(
            "timestamp", column, None, nullable, default=now
        )
        self._columns += (self._last_column,)
        return self

    def timestamps(self):
        """Creates `created_at` and `updated_at` timestamp columns.

        Returns:
            self
        """
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
        """Sets a column to be the decimal representation for the table.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            length {int} -- The total length of the decimal number (default: {17})
            precision {int} -- The number of places that should be used for floating numbers. (default: {6})
            nullable {bool} -- Whether the column is nullable (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column(
            "decimal", column, "{}, {}".format(length, precision), nullable
        )
        self._columns += (self._last_column,)
        return self

    def double(self):
        pass

    def enum(self, column, options=[], nullable=False):
        """Sets a column to be the enum representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            options {list} -- A list of available options for the enum. (default: {False})
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        new_options = ""
        for option in options:
            new_options += "'{}',".format(option)
        new_options = new_options.rstrip(",")
        self._last_column = self.new_column("enum", column, new_options, nullable)
        self._columns += (self._last_column,)
        return self

    def text(self, column, length=None, nullable=False):
        """Sets a column to be the text representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            length {int} -- The length of the column if any. (default: {False})
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("text", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def unsigned(self, column, length=None, nullable=False):
        """Sets a column to be the unsigned integer representation for the table.

        Arguments:
            column {string} -- The column name.

        Keyword Arguments:
            length {int} -- The length of the column. (default: {False})
            nullable {bool} -- Whether the column is nullable. (default: {False})

        Returns:
            self
        """
        self._last_column = self.new_column("unsigned", column, length, nullable)
        self._columns += (self._last_column,)
        return self

    def unsigned_integer(self):
        pass

    def to_sql(self):
        """Compiles the blueprint class into a sql statement.

        Returns:
            string -- The SQL statement generated.
        """
        if self._action == "create":
            return (
                self.grammar(
                    creates=self._columns,
                    constraints=self._constraints,
                    foreign_keys=self._foreign_keys,
                    table=self.table,
                )
                ._compile_create()
                .to_sql()
            )
        else:
            return (
                self.grammar(
                    creates=self._columns,
                    constraints=self._constraints,
                    foreign_keys=self._foreign_keys,
                    table=self.table,
                )
                ._compile_alter()
                .to_sql()
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def nullable(self):
        """Sets the last column created as nullable

        Returns:
            self
        """
        self._last_column.nullable()
        return self

    def change(self):
        """Sets the column to be set to modify instead of altering.

        Returns:
            self
        """
        self._last_column.change()
        return self

    def unique(self, column=None):
        """Sets the last column to be unique if no column name is passed.

        If a column name is passed this method will create a new unique column.

        Keyword Arguments:
            column {string} -- The name of the column. (default: {None})

        Returns:
            self
        """
        if column is None:
            column = self._last_column.column_name

        self._constraints += (Constraint(column, constraint_type="unique"),)

        return self

    def index(self, column):
        """Creates a constraint based on the index constraint representation of the table.

        Arguments:
            column {string} -- The name of the column to create the index on.

        Returns:
            self
        """
        self._constraints += (Constraint(column, constraint_type="index"),)
        return self

    def fulltext(self, column):
        """Creates a constraint based on the full text constraint representation of the table.

        Arguments:
            column {string} -- The name of the column to create the index on.

        Returns:
            self
        """
        self._constraints += (Constraint(column, constraint_type="fulltext"),)
        return self

    def primary(self, column):
        """Creates a constraint based on the primary key constraint representation of the table.

        Arguments:
            column {string} -- The name of the column to create the index on.

        Returns:
            self
        """
        self._constraints += (Constraint(column, constraint_type="primary"),)
        return self

    def foreign(self, column):
        """Starts the creation of a foreign key constraint

        Arguments:
            column {string} -- The name of the column to create the index on.

        Returns:
            self
        """
        self._last_foreign = ForeignKey(column, self.table)
        return self

    def references(self, column):
        """Sets the other column on the foreign table that the local column will use to reference.

        Arguments:
            column {string} -- The name of the column to create the index on.

        Returns:
            self
        """
        self._last_foreign.references(column)
        return self

    def on(self, table):
        """Sets the foreign table that the local column will use to reference on.

        Arguments:
            table {string} -- The foreign table name.

        Returns:
            self
        """
        self._last_foreign.on(table)
        self._foreign_keys += (self._last_foreign,)
        return self

    def on_delete(self, action):
        """Sets the last foreign key to a specific on delete action.

        Arguments:
            action {string} -- The specific action to do on delete.

        Returns:
            self
        """
        self._last_foreign.on_delete(action)
        return self

    def on_update(self, action):
        """Sets the last foreign key to a specific on update action.

        Arguments:
            action {string} -- The specific action to do on update.

        Returns:
            self
        """
        self._last_foreign.on_update(action)
        return self

    def rename(self, old_column, new_column):
        """Rename a column from the old value to a new value.

        Arguments:
            old_column {string} -- The name of the original old column name.
            new_column {string} -- The name of the new column name.

        Returns:
            self
        """
        self._last_column = self.new_column(
            None, new_column, action="rename", length=None, nullable=True
        ).rename(old_column)
        self._columns += (self._last_column,)
        return self

    def after(self, old_column):
        """Sets the column that this new column should be created after.

        This is useful for setting the location of the new column in the table schema.

        Arguments:
            old_column {string} -- The column that this new column should be created after

        Returns:
            self
        """
        self._last_column.after(old_column)
        return self

    def drop_column(self, *columns):
        """Sets columns that should be dropped

        Returns:
            self
        """
        for column in columns:
            self._last_column = self.new_column(None, column, None, None, action="drop")
            self._columns += (self._last_column,)

        return self

    def drop_index(self, indexes):
        """Specifies indexes that should be dropped.

        Arguments:
            indexes {list|string} -- Either a list of indexes or a specific index.

        Returns:
            self
        """
        if isinstance(indexes, str):
            indexes = [indexes]

        for index in indexes:
            self._last_column = self.new_column(
                None, index, None, None, action="drop_index"
            )
            self._columns += (self._last_column,)
        return self

    def drop_unique(self, indexes):
        """Drops a unique index.

        Arguments:
            indexes {list|string} -- Either a list of indexes or a specific index.

        Returns:
            self
        """
        if isinstance(indexes, str):
            indexes = [indexes]

        for index in indexes:
            self._last_column = self.new_column(
                None, index, None, None, action="drop_unique"
            )
            self._columns += (self._last_column,)
        return self

    def drop_primary(self):
        """Drops a primary key index.

        Returns:
            self
        """
        self._last_column = self.new_column(
            None, None, None, None, action="drop_primary"
        )
        self._columns += (self._last_column,)
        return self

    def drop_foreign(self, indexes):
        """Drops foreign key indexes.

        Arguments:
            indexes {list|string} -- Either a list of indexes or a specific index.

        Returns:
            self
        """
        if isinstance(indexes, str):
            indexes = [indexes]

        for key in indexes:
            if not key.startswith(self.table):
                key = self.table + "_" + key
            if not key.endswith("foreign"):
                key = key + "_foreign"

            self._last_column = self.new_column(
                None, key, None, None, action="drop_foreign"
            )
            self._last_column.is_constraint = True
            self._columns += (self._last_column,)
        return self
