from .BaseRelationship import BaseRelationship
from ..collection import Collection


class HasMany(BaseRelationship):
    """Has Many Relationship Class."""

    def apply_query(self, foreign, owner):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        result = foreign.where(
            self.foreign_key, owner.__attributes__[self.local_key]
        ).get()

        return result

    def get_related(self, relation, eagers=None):
        eagers = eagers or []
        builder = self.get_builder().with_(eagers)
        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.pluck(self.local_key).unique(),
            ).get()
        else:
            return builder.where(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.get_primary_key_value(),
            ).get()

    def register_related(self, key, model, collection):
        model.add_relation(
            {key: collection.where(self.foreign_key, model.get_primary_key_value())}
        )
