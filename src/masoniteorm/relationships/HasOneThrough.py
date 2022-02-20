from .BaseRelationship import BaseRelationship
from ..collection import Collection
from inflection import singularize
from ..models.Pivot import Pivot
import pendulum


class HasOneThrough(BaseRelationship):
    """Has Many Relationship Class."""

    def __init__(
        self,
        fn=None,
        local_foreign_key=None,
        other_foreign_key=None,
        local_owner_key=None,
        other_owner_key=None,
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

    def set_keys(self, owner, attribute):
        self.local_key = self.local_key or "id"
        self.foreign_key = self.foreign_key or f"{attribute}_id"
        return self

    def __get__(self, instance, owner):
        """This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """
        attribute = self.fn.__name__
        self.attribute = attribute
        relationship1 = self.fn(self)[0]()
        relationship2 = self.fn(self)[1]()
        self.set_keys(instance, attribute)
        self.distant_builder = relationship1.builder
        self.intermediary_builder = relationship2.builder

        if instance.is_loaded():
            if attribute in instance._relationships:
                return instance._relationships[attribute]

            result = self.apply_query(
                self.distant_builder, self.intermediary_builder, instance
            )
            return result
        else:
            return self

    def apply_query(self, distant_builder, intermediary_builder, owner):
        """Apply the query and return a dictionary to be hydrated.
            Used during accessing a relationship on a model

        Arguments:
            query {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        # select * from `countries` inner join `ports` on `ports`.`country_id` = `countries`.`country_id` where `ports`.`port_id` is null and `countries`.`deleted_at` is null and `ports`.`deleted_at` is null
        distant_builder.join(f"ports", "ports.country_id", "=", "countries.country_id")

        return self

    def get_builder(self):
        return self.distant_builder

    def make_builder(self, eagers=None):
        builder = self.get_builder().with_(eagers)

        return builder

    def make_query(self, query, relation, eagers=None):
        print("make query")
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

        if isinstance(relation, Collection):
            final_result = result.where_in(
                self.local_owner_key,
                relation.pluck(self.local_owner_key, keep_nulls=False),
            ).get()
        else:
            final_result = result.where(
                self.local_owner_key, getattr(relation, self.local_owner_key)
            ).get()

        return final_result

    def get_related(self, query, relation, eagers=None):
        print("get related", query)
        builder = self.distant_builder

        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.pluck(self.local_key, keep_nulls=False).unique(),
            ).get()
        else:
            result = builder.where(
                f"{builder.get_table_name()}.{self.foreign_key}",
                getattr(relation, self.local_owner_key),
            ).first()
            return result

        # return final_result

    def register_related(self, key, model, collection):
        model.add_relation(
            {
                key: collection.where(
                    f"{self._table}_id", getattr(model, self.local_owner_key)
                )
            }
        )

    def get_where_exists_query(self, current_query_builder, callback):
        query = self.distant_builder

        current_query_builder.where_exists(
            query.join(
                "ports", "ports.country_id", "=", "countries.country_id"
            ).where_column("inbound_shipments.from_port_id", "ports.port_id")
        ).when(callback, lambda q: (callback(q)))

    def get_pivot_table_name(self, query, builder):
        pivot_tables = [
            singularize(query.get_table_name()),
            singularize(builder.get_table_name()),
        ]
        pivot_tables.sort()
        return "_".join(pivot_tables)

    def get_with_count_query(self, builder, callback):
        query = self.distant_builder

        if not builder._columns:
            builder = builder.select("*")

        return_query = builder.add_select(
            f"{self.attribute}_count",
            lambda q: (
                (
                    q.count("*")
                    .join("ports", "ports.country_id", "=", "countries.country_id")
                    .where_column("inbound_shipments.from_port_id", "ports.port_id")
                    .table(query.get_table_name())
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

        if self.with_timestamps:
            data.update(
                {
                    "created_at": pendulum.now().to_datetime_string(),
                    "updated_at": pendulum.now().to_datetime_string(),
                }
            )

        return (
            Pivot.on(current_model.builder.connection)
            .table(self._table)
            .without_global_scopes()
            .create(data)
        )

    def attach_related(self, current_model, related_record):
        data = {
            self.local_key: getattr(current_model, self.local_owner_key),
            self.foreign_key: getattr(related_record, self.other_owner_key),
        }

        if self.with_timestamps:
            data.update(
                {
                    "created_at": pendulum.now().to_datetime_string(),
                    "updated_at": pendulum.now().to_datetime_string(),
                }
            )

        return (
            Pivot.on(current_model.builder.connection)
            .table(self._table)
            .without_global_scopes()
            .create(data)
        )

    def query_has(self, current_query_builder):
        related_builder = self.get_builder()

        current_query_builder.where_exists(
            self.distant_builder.where_column(
                "inbound_shipments.from_port_id", "ports.port_id"
            ).join(f"ports", "ports.country_id", "=", "countries.country_id")
        )

        return related_builder
