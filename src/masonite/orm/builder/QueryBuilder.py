class QueryBuilder:
    _columns = "*"

    _sql = ""

    _updates = {}

    _wheres = ()
    _order_by = ()

    _aggregates = ()

    _limit = False

    _action = "select"

    def __init__(self, grammer, connection=None, table=""):
        """QueryBuilder initializer
        
        Arguments:
            grammer {masonite.orm.grammer.Grammer} -- A grammer class.
        
        Keyword Arguments:
            connection {masonite.orm.connection.Connection} -- A connection class (default: {None})
            table {str} -- the name of the table (default: {""})
        """
        self.grammer = grammer
        self.table = table
        self.connection = connection

    def select(self, *args):
        self._columns = list(args)
        return self

    def create(self, creates):
        self._columns = creates
        self._action = "insert"
        return self

    def delete(self, column, value):
        self.where(column, value)
        self._action = "delete"
        return self

    def where(self, column, value):
        self._wheres += ((column, "=", value),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

    def update(self, updates):
        self._updates = updates
        self._action = "update"
        return self

    def sum(self, column):
        self.aggregate("SUM", "{column}".format(column=column))
        return self

    def max(self, column):
        self.aggregate("MAX", "{column}".format(column=column))
        return self

    def order_by(self, column, direction="ASC"):
        self._order_by += ((column, direction),)
        return self

    def aggregate(self, aggregate, column):
        self._aggregates += ((aggregate, column),)

    def first(self):
        return (
            self.connection()
            .make_connection()
            .query(self.limit(1).to_sql(), (), results=1)
        )

    def all(self):
        return self.connection().make_connection().query(self.to_sql(), ())

    def get(self):
        self._action = "select"
        return self.connection().make_connection().query(self.to_sql(), ())

    def to_sql(self):
        grammer = self.grammer(
            columns=self._columns,
            table=self.table,
            wheres=self._wheres,
            limit=self._limit,
            updates=self._updates,
            aggregates=self._aggregates,
            order_by=self._order_by,
        )

        return getattr(
            grammer, "_compile_{action}".format(action=self._action)
        )().to_sql()
