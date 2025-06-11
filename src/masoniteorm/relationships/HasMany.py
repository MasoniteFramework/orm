from ..collection import Collection
from .BaseRelationship import BaseRelationship


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
            {
                key: collection.get(getattr(model, self.local_key))
                or Collection()
            }
        )

    def map_related(self, related_result):
        return related_result.group_by(self.foreign_key)

    def attach(self, current_model, related_record):
        local_key_value = getattr(current_model, self.local_key)
        if not related_record.is_created():
            related_record.fill({self.foreign_key: local_key_value})
            return related_record.create(
                related_record.all_attributes(), cast=True
            )

        related_record.update({self.foreign_key: local_key_value})
        return related_record

    def get_related(self, query, relation, eagers=None, callback=None):
        eagers = eagers or []
        builder = self.get_builder().with_(eagers)

        if callback:
            callback(builder)
        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                Collection(relation._get_value(self.local_key)).unique(),
            ).get()

        return builder.where(
            f"{builder.get_table_name()}.{self.foreign_key}",
            getattr(relation, self.local_key),
        ).get()
