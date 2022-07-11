from .BaseRelationship import BaseRelationship
from ..collection import Collection


class BelongsTo(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, fn, local_key=None, foreign_key=None):
        if isinstance(fn, str):
            self.fn = None
            self.local_key = fn or "id"
            self.foreign_key = local_key
        else:
            self.fn = fn
            self.local_key = local_key or "id"
            self.foreign_key = foreign_key

    def set_keys(self, owner, attribute):
        self.local_key = self.local_key or f"{attribute}_id"
        self.foreign_key = self.foreign_key or "id"
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

    def register_related(self, key, model, collection):
        related = collection.where(
            self.foreign_key, getattr(model, self.local_key)
        ).first()

        model.add_relation({key: related or None})
