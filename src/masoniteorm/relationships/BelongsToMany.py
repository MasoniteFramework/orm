import pendulum
from inflection import singularize

from ..collection import Collection
from .BaseRelationship import BaseRelationship
from src.masoniteorm.models.Pivot import Pivot


class BelongsToMany(BaseRelationship):
    """Has Many Relationship Class."""

    def __init__(
        self,
        fn=None,
        local_key=None,
        foreign_key=None,
        local_owner_key=None,
        other_owner_key=None,
        table=None,
        with_timestamps=False,
        pivot_id="id",
        attribute="pivot",
        with_fields=[],
    ):
        self.fn = fn if not isinstance(fn, str) else None
        self.local_key = local_key
        self.foreign_key = foreign_key
        self.local_owner_key = local_owner_key or "id"
        self.other_owner_key = other_owner_key or "id"
        self._table = table
        self.with_timestamps = with_timestamps
        self._as = attribute
        self.pivot_id = pivot_id
        self.with_fields = with_fields

    def apply_query(self, query, owner):
        """Apply the query to the builder instance.

        Args:
            query (QueryBuilder): The query builder instance
            owner (Model): The model instance

        Returns:
            QueryBuilder
        """
        if isinstance(owner, Collection):
            owner = owner.first()

        if not owner:
            return query.where("0", "=", "1")

        return (
            query.select(
                f"{self.get_related_table()}.*",
                f"{self._table}.{self.local_key} as {self._table}_{self.local_key}",
                f"{self._table}.{self.foreign_key} as {self._table}_{self.foreign_key}",
            )
            .join(
                self._table,
                f"{self._table}.{self.local_key}",
                "=",
                f"{owner.get_table_name()}.{self.local_owner_key}",
            )
            .join(
                self.get_related_table(),
                f"{self._table}.{self.foreign_key}",
                "=",
                f"{self.get_related_table()}.{self.other_owner_key}",
            )
            .where(f"{owner.get_table_name()}.{self.local_owner_key}", "in", [getattr(owner, self.local_owner_key)])
        )

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
        elif self.local_key is None or self.foreign_key is None:
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
                f"{table1}.{self.local_owner_key}",
                Collection(relation._get_value(self.local_owner_key)).unique(),
            ).get()
        else:
            return result.where(
                f"{table1}.{self.local_owner_key}",
                getattr(relation, self.local_owner_key),
            ).get()

    def get_related(self, query, relation, eagers=None, callback=None):
        """Gets the relation needed between the relation and the related builder. If the relation is a collection
        then will need to pluck out all the keys from the collection and fetch from the related builder. If
        relation is just a Model then we can just call the model based on the value of the related
        builders primary key.

        Args:
            relation (Model|Collection):

        Returns:
            Model|Collection
        """
        eagers = eagers or []
        builder = self.get_builder().with_(eagers)

        if callback:
            callback(builder)

        if not self._table:
            # Get table name from builder instead of query when query is a Collection
            table_name = builder.get_table_name()
            pivot_tables = [
                singularize(table_name),
                singularize(relation[0].get_table_name() if isinstance(relation, Collection) else relation.get_table_name()),
            ]
            pivot_tables.sort()
            pivot_table_1, pivot_table_2 = pivot_tables
            self._table = "_".join(pivot_tables)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"
        elif self.local_key is None or self.foreign_key is None:
            pivot_table_1, pivot_table_2 = self._table.split("_", 1)
            self.foreign_key = self.foreign_key or f"{pivot_table_1}_id"
            self.local_key = self.local_key or f"{pivot_table_2}_id"

        table2 = builder.get_table_name()
        table1 = relation[0].get_table_name() if isinstance(relation, Collection) else relation.get_table_name()

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
                f"{table1}.{self.local_owner_key}",
                Collection(relation._get_value(self.local_owner_key)).unique(),
            ).get()
        else:
            return result.where(
                f"{table1}.{self.local_owner_key}",
                getattr(relation, self.local_owner_key),
            ).get()

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
        elif self.local_key is None or self.foreign_key is None:
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
        """Register the related models on the model.

        Args:
            key: The name of the relationship
            model: The model to register the relationship on
            collection: The collection of related models
        """
        if not collection:
            model.add_relation({key: Collection([])})
            return

        # Filter the collection to only include models related to this model
        related = collection.where(
            f"{self._table}_id", getattr(model, self.local_owner_key)
        )
        model.add_relation({key: related})

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
        elif self.local_key is None or self.foreign_key is None:
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
        """Attach a related record to the current model.

        Args:
            current_model (Model): The current model instance
            related_record (Model): The related model instance

        Returns:
            Model
        """
        print(f"[DEBUG] local_key: {self.local_key}, foreign_key: {self.foreign_key}, local_owner_key: {self.local_owner_key}, other_owner_key: {self.other_owner_key}")
        data = {
            self.local_key: getattr(current_model, self.local_owner_key),
            self.foreign_key: getattr(related_record, self.other_owner_key),
        }
        print("BelongsToMany.attach data:", data)
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

    def get_builder(self):
        related_model_class = self.fn(self)
        if not hasattr(self, '_related_builder') or self._related_builder is None:
            self._related_builder = related_model_class().get_builder()
        return self._related_builder
