class Constraint:
    def __init__(self, name, constraint_type, columns=None):
        self.name = name
        self.constraint_type = constraint_type
        self.columns = columns or []
