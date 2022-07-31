from .BaseRelationship import BaseRelationship
from ..collection import Collection
from inflection import singularize
from ..models.Pivot import Pivot
import pendulum


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
        with_fields=[],
    ):
        if isinstance(fn, str):
            self.fn = None
            self.local_key = fn
            self.foreign_key = local_foreign_key
            self.local_owner_key = other_foreign_key or "id"
            self.other_owner_key = local_owner_key or "id"
        else:
            self.fn = fn
            self.local_key = local_foreign_key
            self.foreign_key = other_foreign_key
            self.local_owner_key = local_owner_key or "id"
            self.other_owner_key = other_owner_key or "id"

        self._table = table
        self.with_timestamps = with_timestamps
        self._as = attribute
        self.pivot_id = pivot_id
        self.with_fields = with_fields

    def set_keys(self, owner, attribute):
        self.local_key = self.local_key or "id"
        self.foreign_key = self.foreign_key or f"{attribute}_id"
        return self

    def apply_query(self, query, owner):
        """Apply the query and return a dictionary to be hydrated.
            Used during accessing a relationship on a model

        Arguments:
            query {oject} -- The relationship object
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
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"

        table1 = owner.get_table_name()
        table2 = query.get_table_name()
        result = query.select(
            f"{query.get_table_name()}.*",
            f"{self._table}.{self.local_key} as {self._table}_id",
            f"{self._table}.{self.foreign_key} as m_reserved2",
        ).table(f"{table1}")

        if self.pivot_id:
            result.select(f"{self._table}.{self.pivot_id} as m_reserved3")

        if self.with_timestamps:
            result.select(
                f"{self._table}.updated_at as m_reserved4",
                f"{self._table}.created_at as m_reserved5",
            )

        result.join(
            f"{self._table}",
            f"{self._table}.{self.local_key}",
            "=",
            f"{table1}.{self.local_owner_key}",
        )
        result.join(
            f"{table2}",
            f"{self._table}.{self.foreign_key}",
            "=",
            f"{table2}.{self.other_owner_key}",
        )

        if hasattr(owner, self.local_owner_key):
            result.where(
                f"{table1}.{self.local_owner_key}", getattr(owner, self.local_owner_key)
            )

        if self.with_fields:
            for field in self.with_fields:
                result.select(f"{self._table}.{field}")

        result = result.get()

        for model in result:
            pivot_data = {
                self.local_key: getattr(model, f"{self._table}_id"),
                self.foreign_key: getattr(model, "m_reserved2"),
            }

            if self.with_timestamps:
                pivot_data = {
                    "created_at": getattr(model, "m_reserved5"),
                    "updated_at": getattr(model, "m_reserved4"),
                }

                model.delete_attribute("m_reserved4")
                model.delete_attribute("m_reserved5")

            model.delete_attribute("m_reserved2")

            if self.pivot_id:
                pivot_data.update({self.pivot_id: getattr(model, "m_reserved3")})
                model.delete_attribute("m_reserved3")

            if self.with_fields:
                for field in self.with_fields:
                    pivot_data.update({field: getattr(model, field)})
                    model.delete_attribute(field)

            model.__original_attributes__.update(
                {
                    self._as: (
                        Pivot.on(query.connection)
                        .table(self._table)
                        .hydrate(pivot_data)
                        .activate_timestamps(self.with_timestamps)
                    )
                }
            )

        return result

    def table(self, table):
        self._table = table
        return self

    def make_builder(self, eagers=None):
        builder = self.get_builder().with_(eagers)

        return builder

    def make_query(self, query, relation, eagers=None, callback=None):
        """Used during eager loading a relationship

        Args:
            query ([type]): [description]
            relation ([type]): [description]
            eagers (list, optional): List of eager loaded relationships. Defaults to None.

        Returns:
            [type]: [description]
        """
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
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"

        table2 = builder.get_table_name()
        table1 = query.get_table_name()
        result = (
            builder.select(
                f"{table2}.*",
                f"{self._table}.{self.local_key} as {self._table}_id",
                f"{self._table}.{self.foreign_key} as m_reserved2",
            )
            .run_scopes()
            .table(f"{table1}")
        )

        if self.with_fields:
            for field in self.with_fields:
                result.select(f"{self._table}.{field}")

        result.join(
            f"{self._table}",
            f"{self._table}.{self.local_key}",
            "=",
            f"{table1}.{self.local_owner_key}",
        )

        result.join(
            f"{table2}",
            f"{self._table}.{self.foreign_key}",
            "=",
            f"{table2}.{self.other_owner_key}",
        )

        if self.with_timestamps:
            result.select(
                f"{self._table}.updated_at as m_reserved4",
                f"{self._table}.created_at as m_reserved5",
            )

        if self.pivot_id:
            result.select(f"{self._table}.{self.pivot_id} as m_reserved3")

        result.without_global_scopes()

        if callback:
            callback(result)

        if isinstance(relation, Collection):
            return result.where_in(
                self.local_owner_key,
                Collection(relation._get_value(self.local_owner_key)).unique(),
            ).get()
        else:
            return result.where(
                self.local_owner_key, getattr(relation, self.local_owner_key)
            ).get()

    def get_related(self, query, relation, eagers=None, callback=None):
        final_result = self.make_query(
            query, relation, eagers=eagers, callback=callback
        )
        builder = self.make_builder(eagers)

        for model in final_result:
            pivot_data = {
                self.local_key: getattr(model, f"{self._table}_id"),
                self.foreign_key: getattr(model, "m_reserved2"),
            }

            model.delete_attribute("m_reserved2")

            if self.with_timestamps:
                pivot_data.update(
                    {
                        "updated_at": getattr(model, "m_reserved4"),
                        "created_at": getattr(model, "m_reserved5"),
                    }
                )

            if self.pivot_id:
                pivot_data.update({self.pivot_id: getattr(model, "m_reserved3")})
                model.delete_attribute("m_reserved3")

            if self.with_fields:
                for field in self.with_fields:
                    pivot_data.update({field: getattr(model, field)})
                    model.delete_attribute(field)

            model.__original_attributes__.update(
                {
                    self._as: (
                        Pivot.on(builder.connection)
                        .table(self._table)
                        .hydrate(pivot_data)
                        .activate_timestamps(self.with_timestamps)
                    )
                }
            )

        return final_result

    def relate(self, related_record):
        owner = related_record.get_builder()
        query = self.get_builder()

        if not self._table:
            pivot_tables = [
                singularize(owner.builder.get_table_name()),
                singularize(query.get_table_name()),
            ]
            pivot_tables.sort()
            pivot_table_1, pivot_table_2 = pivot_tables
            self._table = "_".join(pivot_tables)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"

        table1 = owner.get_table_name()
        table2 = query.get_table_name()
        result = query.select(
            f"{query.get_table_name()}.*",
            f"{self._table}.{self.local_key} as {self._table}_id",
            f"{self._table}.{self.foreign_key} as m_reserved2",
        ).table(f"{table1}")

        if self.pivot_id:
            result.select(f"{self._table}.{self.pivot_id} as m_reserved3")

        if self.with_timestamps:
            result.select(
                f"{self._table}.updated_at as m_reserved4",
                f"{self._table}.created_at as m_reserved5",
            )

        result.join(
            f"{self._table}",
            f"{self._table}.{self.local_key}",
            "=",
            f"{table1}.{self.local_owner_key}",
        )
        result.join(
            f"{table2}",
            f"{self._table}.{self.foreign_key}",
            "=",
            f"{table2}.{self.other_owner_key}",
        )

        if hasattr(owner, self.local_owner_key):
            result.where(
                f"{table1}.{self.local_owner_key}", getattr(owner, self.local_owner_key)
            )

        if self.with_fields:
            for field in self.with_fields:
                result.select(f"{self._table}.{field}")

        return result

    def register_related(self, key, model, collection):
        model.add_relation(
            {
                key: collection.where(
                    f"{self._table}_id", getattr(model, self.local_owner_key)
                )
            }
        )

    def joins(self, builder, clause=None):
        if not self._table:
            pivot_tables = [
                singularize(self.get_builder().get_table_name()),
                singularize(builder.get_table_name()),
            ]
            pivot_tables.sort()
            pivot_table_1, pivot_table_2 = pivot_tables
            self._table = "_".join(pivot_tables)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"
        else:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"

        query = self.get_builder()
        table1 = query.get_table_name()
        table2 = builder.get_table_name()
        result = builder
        if not builder._columns:
            result = result.select(
                f"{table2}.*",
                f"{self._table}.{self.local_key} as {self._table}_id",
                f"{self._table}.{self.foreign_key} as m_reserved2",
            )

            if self.pivot_id:
                result.select(f"{self._table}.{self.pivot_id} as m_reserved3")

            if self.with_timestamps:
                result.select(
                    f"{self._table}.updated_at as m_reserved4",
                    f"{self._table}.created_at as m_reserved5",
                )

            if self.with_fields:
                for field in self.with_fields:
                    result.select(f"{self._table}.{field}")
        # Join pivot table with an inner join
        result.join(
            f"{self._table}",
            f"{self._table}.{self.local_key}",
            "=",
            f"{table2}.{self.local_owner_key}",
            clause="inner",
        )

        result.join(
            f"{table1}",
            f"{self._table}.{self.local_owner_key}",
            "=",
            f"{table1}.{self.other_owner_key}",
            clause=clause,
        )

        if self.with_fields:
            for field in self.with_fields:
                result.select(f"{self._table}.{field}")

        return result

    def query_where_exists(self, builder, callback, method="where_exists"):
        query = self.get_builder()
        pivot_table = self._table or self.get_pivot_table_name(query, builder)
        table = self.get_builder().get_table_name()

        getattr(builder, method)(
            query.new()
            .table(table)
            .join(
                f"{pivot_table}",
                f"{table}.{self.other_owner_key}",
                "=",
                f"{pivot_table}.{self.foreign_key}",
            )
            .where_column(
                f"{pivot_table}.{self.local_key}",
                f"{builder.get_table_name()}.{self.local_owner_key}",
            )
            .where_in(
                self.other_owner_key, callback(query.select(self.other_owner_key))
            )
        )

    def query_has(self, builder, method="where_exists"):
        query = self.get_builder()
        pivot_table = self._table or self.get_pivot_table_name(query, builder)
        table = self.get_builder().get_table_name()
        return getattr(builder, method)(
            query.new()
            .table(table)
            .join(
                f"{pivot_table}",
                f"{table}.{self.other_owner_key}",
                "=",
                f"{pivot_table}.{self.foreign_key}",
            )
            .where_column(
                f"{pivot_table}.{self.local_key}",
                f"{builder.get_table_name()}.{self.local_owner_key}",
            )
        )

    def get_pivot_table_name(self, query, builder):
        pivot_tables = [
            singularize(query.get_table_name()),
            singularize(builder.get_table_name()),
        ]
        pivot_tables.sort()
        return "_".join(pivot_tables)

    def get_with_count_query(self, builder, callback):
        query = self.get_builder()
        self._table = self._table or self.get_pivot_table_name(query, builder)

        if not builder._columns:
            builder = builder.select("*")

        return_query = builder.add_select(
            f"{query.get_table_name()}_count",
            lambda q: (
                (
                    q.count("*")
                    .where_column(
                        f"{builder.get_table_name()}.{self.local_owner_key}",
                        f"{self._table}.{self.local_key}",
                    )
                    .table(self._table)
                    .when(
                        callback,
                        lambda q: (
                            q.where_in(
                                self.foreign_key,
                                callback(query.select(self.other_owner_key)),
                            )
                        ),
                    )
                )
            ),
        )

        return return_query

    def attach(self, current_model, related_record):
        data = {
            self.local_key: getattr(current_model, self.local_owner_key),
            self.foreign_key: getattr(related_record, self.other_owner_key),
        }

        self._table = self._table or self.get_pivot_table_name(
            current_model, related_record
        )

        if self.with_timestamps:
            data.update(
                {
                    "created_at": pendulum.now().to_datetime_string(),
                    "updated_at": pendulum.now().to_datetime_string(),
                }
            )

        return (
            Pivot.on(current_model.get_builder().connection)
            .table(self._table)
            .without_global_scopes()
            .create(data)
        )

    def detach(self, current_model, related_record):
        data = {
            self.local_key: getattr(current_model, self.local_owner_key),
            self.foreign_key: getattr(related_record, self.other_owner_key),
        }

        self._table = self._table or self.get_pivot_table_name(
            current_model, related_record
        )

        return (
            Pivot.on(current_model.get_builder().connection)
            .table(self._table)
            .without_global_scopes()
            .where(data)
            .delete()
        )

    def attach_related(self, current_model, related_record):
        data = {
            self.local_key: getattr(current_model, self.local_owner_key),
            self.foreign_key: getattr(related_record, self.other_owner_key),
        }

        self._table = self._table or self.get_pivot_table_name(
            current_model, related_record
        )

        if self.with_timestamps:
            data.update(
                {
                    "created_at": pendulum.now().to_datetime_string(),
                    "updated_at": pendulum.now().to_datetime_string(),
                }
            )

        return (
            Pivot.table(self._table)
            .on(current_model.get_builder().connection)
            .without_global_scopes()
            .create(data)
        )

    def detach_related(self, current_model, related_record):
        data = {
            self.local_key: getattr(current_model, self.local_owner_key),
            self.foreign_key: getattr(related_record, self.other_owner_key),
        }

        self._table = self._table or self.get_pivot_table_name(
            current_model, related_record
        )

        if self.with_timestamps:
            data.update(
                {
                    "created_at": pendulum.now().to_datetime_string(),
                    "updated_at": pendulum.now().to_datetime_string(),
                }
            )

        return (
            Pivot.on(current_model.get_builder().connection)
            .table(self._table)
            .without_global_scopes()
            .where(data)
            .delete()
        )
