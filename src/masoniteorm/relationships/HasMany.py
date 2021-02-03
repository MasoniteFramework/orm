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

    def get_related(self, query, relation, eagers=None):
        eagers = eagers or []
        builder = self.get_builder().with_(eagers)
        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.pluck(self.local_key, keep_nulls=False).unique(),
            ).get()
        else:
            return builder.where(
                f"{builder.get_table_name()}.{self.foreign_key}",
                getattr(relation, self.local_key),
            ).get()

    def register_related(self, key, model, collection):
        model.add_relation(
            {key: collection.where(self.foreign_key, getattr(model, self.local_key))}
        )
