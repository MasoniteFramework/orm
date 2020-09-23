from .BaseRelationship import BaseRelationship
from ..collection import Collection


class HasMany(BaseRelationship):
    """Has Many Relationship Class.
    """

    def apply_query(self, foreign, owner, foreign_key, local_key):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.
            foreign_key {string} -- The column to access on the relationship model.
            local_key {string} -- The column to access on the current model.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        result = foreign.where(foreign_key, owner.__attributes__[local_key]).get()
        return result

    def get_related(self, relation):
        builder = self.get_builder()
        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.pluck(self.local_key),
            ).get()
        else:
            return builder.where(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.get_primary_key_value(),
            ).get()
