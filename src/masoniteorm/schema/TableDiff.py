from .Column import Column

class TableDiff:

    def __init__(self, name):
        self.name = name
        self.from_table = None
        self.new_name = None
        self.removed_indexes = {}
        self.added_columns = {}
        self.removed_constraints = {}

    def from_table(self, from_table):
        self.from_table = from_table
    
    def remove_constraint(self, name):
        self.removed_constraints.update({name: self.from_table.get_constraint(name)})
    
    def get_removed_constraints(self):
        return self.removed_constraints

    def add_column(self, name=None, column_type=None, length=None, nullable=False, default=None):
        self.added_columns.update({name: Column(name, column_type)})
        return self

    def remove_index(self, name):
        self.removed_indexes.update({name: self.from_table.get_index(name)}) 


    

    
