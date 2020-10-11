from .Column import Column
from .ForeignKeyConstraint import ForeignKeyConstraint
from .Constraint import Constraint
from .Index import Index


class TableDiff:
    def __init__(self, name):
        self.name = name
        self.from_table = None
        self.new_name = None
        self.removed_indexes = []
        self.added_indexes = {}
        self.added_columns = {}
        self.dropped_columns = []
        self.dropped_foreign_keys = []
        self.renamed_columns = {}
        self.removed_constraints = {}
        self.added_constraints = {}
        self.added_foreign_keys = {}

    def from_table(self, from_table):
        self.from_table = from_table

    def remove_constraint(self, name):
        self.removed_constraints.update({name: self.from_table.get_constraint(name)})

    def get_removed_constraints(self):
        return self.removed_constraints

    def add_column(
        self, name=None, column_type=None, length=None, nullable=False, default=None
    ):
        column = Column(
            name, column_type, length=length, nullable=nullable, default=default
        )
        self.added_columns.update({name: column})
        return column

    def get_added_columns(self):
        return self.added_columns

    def get_renamed_columns(self):
        return self.renamed_columns

    def rename_column(
        self,
        original_name,
        new_name,
        column_type=None,
        length=None,
        nullable=False,
        default=None,
    ):
        self.renamed_columns.update(
            {
                original_name: Column(
                    new_name,
                    column_type,
                    length=length,
                    nullable=nullable,
                    default=default,
                )
            }
        )

    def remove_index(self, name):
        self.removed_indexes.append(name)

    def add_index(self, column, name, index_type):
        self.added_indexes.update({column: Index(column, name, index_type)})

    def add_constraint(self, name, constraint_type, columns=[]):
        self.added_constraints.update(
            {name: Constraint(name, constraint_type, columns=columns)}
        )

    def get_added_constraints(self):
        return self.added_constraints

    def add_foreign_key(self, column, table=None, foreign_column=None):
        foreign_key = ForeignKeyConstraint(column, table, foreign_column)
        self.added_foreign_keys.update({column: foreign_key})

        return foreign_key

    def get_added_foreign_keys(self):
        return self.added_foreign_keys

    def drop_column(self, name):
        self.dropped_columns.append(name)

    def get_dropped_columns(self):
        return self.dropped_columns

    def get_dropped_foreign_keys(self):
        return self.dropped_foreign_keys

    def drop_foreign(self, name):
        self.dropped_foreign_keys.append(name)
        return self
