from .BaseRelationship import BaseRelationship
from ..collection import Collection


class HasOneThrough(BaseRelationship):
    """HasOneThrough Relationship Class."""

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

    def set_keys(self, distant_builder, intermediary_builder, attribute):
        self.local_key = self.local_key or "id"
        self.foreign_key = self.foreign_key or f"{attribute}_id"
        self.local_owner_key = self.local_owner_key or "id"
        self.other_owner_key = self.other_owner_key or "id"
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
        self.distant_builder = relationship1.builder
        self.intermediary_builder = relationship2.builder
        self.set_keys(self.distant_builder, self.intermediary_builder, attribute)

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
        distant_builder.join(
            f"{self.intermediary_builder.get_table_name()}",
            f"{self.intermediary_builder.get_table_name()}.{self.foreign_key}",
            "=",
            f"{distant_builder.get_table_name()}.{self.other_owner_key}",
        )

        return self

    def get_builder(self):
        return self.distant_builder

    def make_builder(self, eagers=None):
        builder = self.get_builder().with_(eagers)

        return builder

    def get_related(self, query, relation, eagers=None):
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

    def get_where_exists_query(self, current_query_builder, callback):
        query = self.distant_builder

        current_query_builder.where_exists(
            query.join(
                f"{self.intermediary_builder.get_table_name()}",
                f"{self.intermediary_builder.get_table_name()}.{self.foreign_key}",
                "=",
                f"{query.get_table_name()}.{self.other_owner_key}",
            ).where_column(
                f"{current_query_builder.get_table_name()}.{self.local_owner_key}",
                f"{self.intermediary_builder.get_table_name()}.{self.local_key}",
            )
        ).when(callback, lambda q: (callback(q)))

    def get_with_count_query(self, builder, callback):
        query = self.distant_builder

        if not builder._columns:
            builder = builder.select("*")

        return_query = builder.add_select(
            f"{self.attribute}_count",
            lambda q: (
                (
                    q.count("*")
                    .join(
                        f"{self.intermediary_builder.get_table_name()}",
                        f"{self.intermediary_builder.get_table_name()}.{self.foreign_key}",
                        "=",
                        f"{query.get_table_name()}.{self.other_owner_key}",
                    )
                    .where_column(
                        f"{builder.get_table_name()}.{self.local_owner_key}",
                        f"{self.intermediary_builder.get_table_name()}.{self.local_key}",
                    )
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
        raise NotImplementedError(
            "HasOneThrough relationship does not implement the attach method"
        )

    def attach_related(self, current_model, related_record):
        raise NotImplementedError(
            "HasOneThrough relationship does not implement the attach_related method"
        )

    def query_has(self, current_query_builder):
        related_builder = self.get_builder()

        current_query_builder.where_exists(
            self.distant_builder.where_column(
                f"{current_query_builder.get_table_name()}.{self.local_owner_key}",
                f"{self.intermediary_builder.get_table_name()}.{self.local_key}",
            ).join(
                f"{self.intermediary_builder.get_table_name()}",
                f"{self.intermediary_builder.get_table_name()}.{self.foreign_key}",
                "=",
                f"{self.distant_builder.get_table_name()}.{self.other_owner_key}",
            )
        )

        return related_builder
