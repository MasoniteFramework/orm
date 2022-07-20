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

    def set_keys(self, owner, attribute):
        self.local_key = self.local_key or "id"
        self.foreign_key = self.foreign_key or f"{attribute}_id"
        return self

    def register_related(self, key, model, collection):
        model.add_relation(
            {key: collection.where(self.foreign_key, getattr(model, self.local_key))}
        )
