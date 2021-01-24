from .BaseRelationship import BaseRelationship
from ..collection import Collection
from inflection import singularize, underscore


class BelongsToMany(BaseRelationship):
    """Has Many Relationship Class."""

    def __init__(
        self,
        fn=None,
        local_foreign_key=None,
        other_foreign_key=None,
        local_owner_key=None,
        other_owner_key=None,
        table=None,
    ):
        if isinstance(fn, str):
            self.fn = None
            self.local_foreign_key = fn
            self.other_foreign_key = local_foreign_key
            self.local_owner_key = other_foreign_key
            self.other_owner_key = local_owner_key or "id"
        else:
            self.fn = fn
            self.local_foreign_key = local_foreign_key
            self.other_foreign_key = other_foreign_key
            self.local_owner_key = local_owner_key or "id"
            self.other_owner_key = other_owner_key or "id"

        self._table = table

    def apply_query(self, query, owner):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """

        if not self._table:
            pivot_tables = [
                singularize(owner.builder.get_table_name()),
                singularize(query.get_table_name()),
            ]
            pivot_tables.sort()
            pivot_table_1, pivot_table_2 = pivot_tables
            self._table = "_".join(pivot_tables)
            other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
            local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
            local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"

        result = query.where_in(
            self.other_owner_key,
            lambda q: q.select(other_foreign_key)
            .table(self._table)
            .where(local_foreign_key, owner.__attributes__[self.local_owner_key]),
        )

        return result

    def table(self, table):
        self._table = table
        return self

    def get_related(self, query, relation, eagers=None):
        eagers = eagers or []
        builder = self.get_builder().with_(eagers)

        pivot_tables = [
            singularize(builder.get_table_name()),
            singularize(query.get_table_name()),
        ]

        pivot_tables.sort()
        pivot_table_1, pivot_table_2 = pivot_tables

        other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
        local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"

        if isinstance(relation, Collection):
            return builder.where_in(
                self.other_owner_key,
                lambda q: q.select(other_foreign_key)
                .table("_".join(pivot_tables))
                .where_in(local_foreign_key, relation.pluck(self.local_owner_key)),
            ).get()
        else:
            return builder.where(
                f"{builder.get_table_name()}.{self.local_owner_key}",
                relation.get_primary_key_value(),
            ).get()

    def register_related(self, key, model, collection):
        model.add_relation(
            {
                key: collection.where(
                    self.local_owner_key, getattr(model, self.local_owner_key)
                )
            }
        )
