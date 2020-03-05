from .base import Constraint


class ForeignKeyConstraint(Constraint):

    _type = "foreign_key"

    def __init__(self, foreign_relation):
        """
            :type foreign_relation : ForeignKeyRelation
        """
        self._foreign_relations = foreign_relation

    def to_sql(self, grammar):
        """
            :type grammar : Grammar
        """
        constraint = getattr(grammar, self._get_constraint())()

        for foreign_relation in self._foreign_relations:

            local_columns = _compile_columns(foreign_relation.local_columns)
            external_columns = foreign_relation.external_columns
            foreign_table = foreign_relation.foreign_table

            params = {
                "local_columns": local_columns,
                "external_columns": external_columns,
                "foreign_table": foreign_table,
            }

        return constaint.format(**params) + " "

    def _compile_columns(self, *columns):
        return list(map(grammar._compile_column, list(columns)))


class UniqueConstraint(Constraint):

    _type = "unique"
    
    def __init__(self, column=None):
        self.column = column

    def to_sql(self, grammar):
        """
            :type grammar : Grammar
        """
        constraint = getattr(grammar, self._get_constraint())()

        params = {
            "column": grammar._compile_column(self.column.column_name),
            "clean_column": self.column.column_name,
        }

        return constraint.format(**params)
