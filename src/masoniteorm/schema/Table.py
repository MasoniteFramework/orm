from .Column import Column
from .Constraint import Constraint
from .Index import Index
from .ForeignKeyConstraint import ForeignKeyConstraint


class Table:
    def __init__(self, table):
        self.name = table
        self.added_columns = {}
        self.added_constraints = {}
        self.added_indexes = {}
        self.added_foreign_keys = {}
        self.renamed_columns = {}
        self.drop_indexes = {}
        self.foreign_keys = {}
        self.primary_key = None

    def add_column(
        self,
        name=None,
        column_type=None,
        length=None,
        values=None,
        nullable=False,
        default=None,
    ):
        column = Column(
            name,
            column_type,
            length=length,
            nullable=nullable,
            values=values or [],
            default=default,
        )
        self.added_columns.update({name: column})
        return column

    def add_constraint(self, name, constraint_type, columns=None):
        self.added_constraints.update(
            {name: Constraint(name, constraint_type, columns=columns or [])}
        )

    def add_foreign_key(self, column, table=None, foreign_column=None):
        foreign_key = ForeignKeyConstraint(column, table, foreign_column)
        self.added_foreign_keys.update({column: foreign_key})

        return foreign_key

    def get_added_foreign_keys(self):
        return self.added_foreign_keys

    def get_constraint(self, name):
        return self.added_constraints[name]

    def get_added_constraints(self):
        return self.added_constraints

    def get_added_columns(self):
        return self.added_columns

    def get_renamed_columns(self):
        return self.added_columns

    def set_primary_key(self, column_name):
        self.primary_key = column_name
        self.added_columns[column_name].set_as_primary()
        return self

    def add_index(self, column, name, index_type):
        self.added_indexes.update({name: Index(column, name, index_type)})

    def get_index(self, name):
        return self.added_indexes[name]
