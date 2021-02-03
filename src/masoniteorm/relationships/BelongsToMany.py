from .BaseRelationship import BaseRelationship
from ..collection import Collection
from inflection import singularize, underscore
from ..models.Pivot import Pivot


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
        with_timestamps=False,
        pivot_id="id",
        attribute="pivot",
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
        self.with_timestamps = with_timestamps
        self._as = attribute
        self.pivot_id = pivot_id

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
            self.other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
            self.local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
            self.local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"

        table1 = owner.builder.get_table_name()
        table2 = query.get_table_name()
        result = query.select(
            f"{query.get_table_name()}.*",
            f"{self._table}.{self.local_foreign_key}",
            f"{self._table}.{self.other_foreign_key}",
        ).table(f"{table1}")

        if self.pivot_id:
            result.select(f"{self._table}.id as m_reserved_3")

        if self.with_timestamps:
            result.select(
                f"{self._table}.updated_at as m_reserved_1",
                f"{self._table}.created_at as m_reserved_2",
            )

        result.join(
            f"{self._table}",
            f"{self._table}.{self.local_foreign_key}",
            "=",
            f"{table1}.{self.local_owner_key}",
        )
        result.join(
            f"{table2}",
            f"{self._table}.{self.other_foreign_key}",
            "=",
            f"{table2}.{self.other_owner_key}",
        )

        if hasattr(owner, self.local_owner_key):
            result.where(
                f"{table1}.{self.local_owner_key}", getattr(owner, self.local_owner_key)
            )

        result = result.get()

        for p in result:
            pivot_data = {
                self.local_foreign_key: getattr(p, self.local_foreign_key),
                self.other_foreign_key: getattr(p, self.other_foreign_key),
            }

            if self.pivot_id:
                pivot_data.update({self.pivot_id: getattr(p, "m_reserved_3")})

            if self.with_timestamps:
                pivot_data.update(
                    {
                        "updated_at": getattr(p, "m_reserved_1"),
                        "created_at": getattr(p, "m_reserved_2"),
                    }
                )
            setattr(
                p,
                self._as,
                Pivot.on(query.connection)
                .table(self._table)
                .hydrate(pivot_data)
                .activate_timestamps(self.with_timestamps),
            )

        return result

    def table(self, table):
        self._table = table
        return self

    def get_related(self, query, relation, eagers=None):
        eagers = eagers or []
        builder = self.get_builder().with_(eagers)

        if not self._table:
            pivot_tables = [
                singularize(builder.get_table_name()),
                singularize(query.get_table_name()),
            ]
            pivot_tables.sort()
            pivot_table_1, pivot_table_2 = pivot_tables
            self._table = "_".join(pivot_tables)
            self.other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
            self.local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.other_foreign_key = self.other_foreign_key or f"{pivot_table_1}_id"
            self.local_foreign_key = self.local_foreign_key or f"{pivot_table_2}_id"

        table2 = builder.get_table_name()
        table1 = query.get_table_name()
        result = builder.select(
            f"{table2}.*",
            f"{self._table}.{self.local_foreign_key}",
            f"{self._table}.{self.other_foreign_key}",
        ).table(f"{table1}")

        result.join(
            f"{self._table}",
            f"{self._table}.{self.local_foreign_key}",
            "=",
            f"{table1}.{self.local_owner_key}",
        )

        result.join(
            f"{table2}",
            f"{self._table}.{self.other_foreign_key}",
            "=",
            f"{table2}.{self.other_owner_key}",
        )

        if self.with_timestamps:
            result.select(
                f"{self._table}.updated_at as m_reserved_1",
                f"{self._table}.created_at as m_reserved_2",
            )

        if self.pivot_id:
            result.select(f"{self._table}.id as m_reserved_3")

        if isinstance(relation, Collection):
            final_result = result.where_in(
                self.local_owner_key,
                relation.pluck(self.local_owner_key, keep_nulls=False),
            ).get()
        else:
            final_result = result.where(
                self.local_owner_key, getattr(relation, self.local_owner_key)
            ).get()

        for model in final_result:
            pivot_data = {
                self.local_foreign_key: getattr(model, self.local_foreign_key),
                self.other_foreign_key: getattr(model, self.other_foreign_key),
            }

            if self.with_timestamps:
                pivot_data.update(
                    {
                        "updated_at": getattr(p, "m_reserved_1"),
                        "created_at": getattr(p, "m_reserved_2"),
                    }
                )

            if self.pivot_id:
                pivot_data.update({self.pivot_id: getattr(model, "m_reserved_3")})

            setattr(
                model,
                self._as,
                Pivot.on(builder.connection)
                .table(self._table)
                .hydrate(pivot_data)
                .activate_timestamps(self.with_timestamps),
            )

        return final_result

    def register_related(self, key, model, collection):
        model.add_relation(
            {
                key: collection.where(
                    self.local_foreign_key, getattr(model, self.local_owner_key)
                )
            }
        )
