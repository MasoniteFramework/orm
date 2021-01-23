from .BaseRelationship import BaseRelationship
from ..collection import Collection


class BelongsToMany(BaseRelationship):
    """Has Many Relationship Class."""

    def __init__(self, fn, local_key=None, foreign_key=None):
        if isinstance(fn, str):
            self.local_key = fn
            self.foreign_key = local_key
        else:
            self.fn = fn
            self.foreign_key = foreign_key

    def apply_query(self, foreign, owner):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        print('local')
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
