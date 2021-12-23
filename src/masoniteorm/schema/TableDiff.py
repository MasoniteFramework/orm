from .Column import Column
from .Table import Table


class TableDiff(Table):
    def __init__(self, name):
        self.name = name
        self.from_table = None
        self.new_name = None
        self.removed_indexes = []
        self.removed_unique_indexes = []
        self.added_indexes = {}
        self.added_columns = {}
        self.changed_columns = {}
        self.dropped_columns = []
        self.dropped_foreign_keys = []
        self.dropped_primary_keys = []
        self.renamed_columns = {}
        self.removed_constraints = {}
        self.added_constraints = {}
        self.added_foreign_keys = {}
        self.comment = None

    def remove_constraint(self, name):
        self.removed_constraints.update({name: self.from_table.get_constraint(name)})

    def get_removed_constraints(self):
        return self.removed_constraints

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

    def remove_unique_index(self, name):
        self.removed_unique_indexes.append(name)

    def drop_column(self, name):
        self.dropped_columns.append(name)

    def get_dropped_columns(self):
        return self.dropped_columns

    def get_dropped_foreign_keys(self):
        return self.dropped_foreign_keys

    def drop_foreign(self, name):
        self.dropped_foreign_keys.append(name)
        return self

    def drop_primary(self, name):
        self.dropped_primary_keys.append(name)
        return self

    def change_column(self, added_column):
        self.added_columns.pop(added_column.name)

        self.changed_columns.update({added_column.name: added_column})

    def add_comment(self, comment):
        self.comment = comment
        return self
