from .BaseRelationship import BaseRelationship
from ..collection import Collection
from inflection import singularize, underscore


class BelongsToMany(BaseRelationship):
    """Has Many Relationship Class."""

    def __init__(
        self,
        fn,
        local_foreign_key=None,
        other_foreign_key=None,
        local_owner_key="id",
        other_owner_key="id",
    ):
        if isinstance(fn, str):
            self.local_foreign_key = fn
            self.other_foreign_key = local_foreign_key
            self.local_owner_key = other_foreign_key
            self.other_owner_key = local_owner_key
        else:
            self.fn = fn
            # slef.local_foreign_key =
            self.other_foreign_key = other_foreign_key
            self.local_owner_key = local_owner_key
            self.other_owner_key = other_owner_key

    def apply_query(self, query, owner):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        print("local_foreign_key", self.local_foreign_key)
        print("other_foreign_key", self.other_foreign_key)
        print("local_owner_key", self.local_owner_key)
        print("other_owner_key", self.other_owner_key)
        print("builder", self.get_builder())
        print("owner", owner.get_primary_key_value())
        print("query", query)

        pivot_tables = [
            singularize(owner.builder.get_table_name()),
            singularize(query.get_table_name()),
        ]

        pivot_tables.sort()

        result = query.where_in(
            self.other_owner_key,
            lambda q: q.select(self.other_foreign_key)
            .table("_".join(pivot_tables))
            .where(self.local_foreign_key, owner.__attributes__[self.local_owner_key]),
        )

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
