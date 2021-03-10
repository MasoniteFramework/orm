from .BaseRelationship import BaseRelationship
from ..collection import Collection


class HasOne(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, fn, foreign_key=None, local_key=None):
        if isinstance(fn, str):
            self.foreign_key = fn
            self.local_key = foreign_key or "id"
        else:
            self.fn = fn
            self.local_key = local_key or "id"
            self.foreign_key = foreign_key

    def set_keys(self, owner, attribute):
        self.local_key = self.local_key or "id"
        self.foreign_key = self.foreign_key or f"{attribute}_id"
        return self

    def apply_query(self, foreign, owner):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """

        return foreign.where(
            self.foreign_key, owner.__attributes__[self.local_key]
        ).first()

    def get_related(self, query, relation, eagers=()):
        """Gets the relation needed between the relation and the related builder. If the relation is a collection
        then will need to pluck out all the keys from the collection and fetch from the related builder. If
        relation is just a Model then we can just call the model based on the value of the related
        builders primary key.

        Args:
            relation (Model|Collection):

        Returns:
            Model|Collection
        """
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
            ).first()

    def register_related(self, key, model, collection):
        related = collection.where(
            self.foreign_key, getattr(model, self.local_key)
        ).first()

        model.add_relation({key: related or None})
