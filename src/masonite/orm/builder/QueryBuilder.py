class QueryBuilder:
    _columns = "*"

    _sql = ""

    _updates = {}

    _wheres = ()

    _limit = False

    _action = "select"

    def __init__(self, grammer, table=""):
        self.grammer = grammer
        self.table = table

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

    def first(self):
        pass

    def get(self):
        pass

    def to_sql(self):
        grammer = self.grammer(
            columns=self._columns,
            table=self.table,
            wheres=self._wheres,
            limit=self._limit,
            updates=self._updates,
        )
        return getattr(
            grammer, "_compile_{action}".format(action=self._action)
        )().to_sql()
