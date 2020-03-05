class Constraint:

    _type = None

    def to_sql(self, grammar=None):
        raise NotImplementedError()

    def _get_constraint(self):

        self._type = self._type.lower()

        return "{type}_constraint_string".format(type=self._type)

    # @classmethod
    # def make(cls):

    #     types = {
    #         "foreign": ForeignKeyConstraint()
    #         "unique": UniqueConstraint()
    #     }

    #     constraint = types.get(_type, None)

    #     if constraint:
    #         return constraint

    #     raise ValueError("There's no constraint related to {constraint} name.")
