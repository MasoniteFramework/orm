class ForeignKeyConstraint:
    def __init__(self, column, foreign_table, foreign_column):
        self.column = column
        self.foreign_table = foreign_table
        self.foreign_column = foreign_column
