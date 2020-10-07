from .Column import Column
from .Constraint import Constraint

class Table:

    def __init__(self, table):
        self.name = table
        self.added_columns = {}
        self.added_constraints = {}
        self.renamed_columns = {}
        self.drop_indexes = {}
        self.foreign_keys = {}
        self.primary_key = None

    def add_column(self, name=None, column_type=None, length=None, nullable=False, default=None):
        self.added_columns.update({name: Column(name, column_type)})
        return self

    def add_constraint(self, name, constraint_type, columns=[]):
        self.added_constraints.update({name: Constraint(name, constraint_type, columns=columns)})

    def get_constraint(self, name):
        return self.added_constraints[name]

    def get_added_constraints(self):
        return self.added_constraints

    def get_added_columns(self):
        return self.added_columns

    def rename_column(self, column, to):
        pass

    def set_primary_key(self, key):
        self.primary_key = key
        self.added_columns[key].set_as_primary()
        return self

    def add_foreign_key_constraint(self):
        pass

    def add_index(self):
        pass

    def drop_index(self, index):
        pass