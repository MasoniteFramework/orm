from ..blueprint import Blueprint


class ForeignKeyRelation:

    EVENTS = ["UPDATE", "DELETE"]

    ACTIONS = {
        "cascade": "CASCADE",
        "restrict": "RESTRICT",
        "none": "NO ACTION",
        "null": "SET NULL",
        "default": "SET DEFAULT",
    }

    def __init__(self, *local_columns):
        self.foreign_table = None
        self.local_columns = list(local_columns)
        self.external_columns = None
        self.event = None
        self.action = None

    def references(self, *external_columns):
        if not external_columns:
            raise ValueError(
                "You should define foreign key definitions on relationships."
            )

        self.external_columns = list(external_columns)
        return self

    def on(self, table=None):
        self.foreign_table = table
        return self

    def on_delete(self, action):
        self.event = "DELETE"

        if not action.lower() in ACTIONS:
            raise ValueError("This action isn't supported.")

        self.action = ACTIONS.get(action, None)

    def on_update(self, action):
        self.event = "UPDATE"

        if not action.lower() in ACTIONS:
            raise ValueError("This action isn't supported.")

        self.action = ACTIONS.get(action, None)

    @property
    def local_keys(self):
        return _format_columns(self.local_columns)

    @property
    def foreign_keys(self):
        return _format_columns(self.local_columns)

    def _format_column(self, columns):
        column_names = [column.column_name for column in columns]
        return ", ".join(column_names)
