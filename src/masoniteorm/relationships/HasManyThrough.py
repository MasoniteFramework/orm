from ..collection import Collection
from .BaseRelationship import BaseRelationship


class HasManyThrough(BaseRelationship):
    """HasManyThrough Relationship Class."""

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

            result = self.apply_related_query(
                self.distant_builder, self.intermediary_builder, instance
            )
            return result
        else:
            return self

    def apply_related_query(self, distant_builder, intermediary_builder, owner):
        """
        Apply the query to return a Collection of data for the distant models to be hydrated with.

        Method is used when accessing a relationship on a model if its not
        already eager loaded

        Arguments
            distant_builder (QueryBuilder): QueryBuilder attached to the distant table
            intermediate_builder (QueryBuilder): QueryBuilder attached to the intermediate (linking) table
            owner (Any): the model this relationship is starting from

        Returns
            Collection: Collection of  dicts which will be used for hydrating models.
        """

        distant_table = distant_builder.get_table_name()
        intermediate_table = intermediary_builder.get_table_name()

        return (
            self.distant_builder.select(f"{distant_table}.*, {intermediate_table}.{self.local_key}")
            .join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            )
            .where(
                f"{intermediate_table}.{self.local_key}",
                getattr(owner, self.local_owner_key),
            )
            .get()
        )

    def relate(self, related_model):
        return self.distant_builder.join(
            f"{self.intermediary_builder.get_table_name()}",
            f"{self.intermediary_builder.get_table_name()}.{self.foreign_key}",
            "=",
            f"{self.distant_builder.get_table_name()}.{self.other_owner_key}",
        ).where(
            f"{self.intermediary_builder.get_table_name()}.{self.local_key}",
            getattr(related_model, self.local_owner_key),
        )

    def get_builder(self):
        return self.distant_builder

    def make_builder(self, eagers=None):
        builder = self.get_builder().with_(eagers)

        return builder

    def register_related(self, key, model, collection):
        """
        Attach the related model to source models attribute

        Arguments
            key (str): The attribute name
            model (Any): The model instance
            collection (Collection): The data for the related models

        Returns
            None
        """
        related = collection.get(getattr(model, self.local_owner_key), None)
        if related and not isinstance(related, Collection):
            related = Collection(related)

        model.add_relation({key: related if related else None})

    def get_related(self, current_builder, relation, eagers=None, callback=None):
        """
        Get a Collection to hydrate the models for the distant table with
        Used when eager loading the model attribute

        Arguments
            current_builder (QueryBuilder): The source models QueryBuilder object
            relation (HasManyThrough): this relationship object
            eagers (Any):
            callback (Any):

        Returns
             Collection the collection of dicts to hydrate the distant models with
        """

        distant_table = self.distant_builder.get_table_name()
        intermediate_table = self.intermediary_builder.get_table_name()

        if callback:
            callback(current_builder)

        (
            self.distant_builder.select(
                f"{distant_table}.*, {intermediate_table}.{self.local_key}"
            ).join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            )
        )

        if isinstance(relation, Collection):
            return self.distant_builder.where_in(
                f"{intermediate_table}.{self.local_key}",
                Collection(relation._get_value(self.local_owner_key)).unique(),
            ).get()
        else:
            return self.distant_builder.where(
                f"{intermediate_table}.{self.local_key}",
                getattr(relation, self.local_owner_key),
            ).get()

    def attach(self, current_model, related_record):
        raise NotImplementedError(
            "HasOneThrough relationship does not implement the attach method"
        )

    def attach_related(self, current_model, related_record):
        raise NotImplementedError(
            "HasOneThrough relationship does not implement the attach_related method"
        )

    def query_has(self, current_builder, method="where_exists"):
        distant_table = self.distant_builder.get_table_name()
        intermediate_table = self.intermediary_builder.get_table_name()

        getattr(current_builder, method)(
            self.distant_builder.join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            ).where_column(
                f"{intermediate_table}.{self.local_key}",
                f"{current_builder.get_table_name()}.{self.local_owner_key}",
            )
        )

        return self.distant_builder

    def query_where_exists(self, current_builder, callback, method="where_exists"):
        distant_table = self.distant_builder.get_table_name()
        intermediate_table = self.intermediary_builder.get_table_name()

        getattr(current_builder, method)(
            self.distant_builder.join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            )
            .where_column(
                f"{intermediate_table}.{self.local_key}",
                f"{current_builder.get_table_name()}.{self.local_owner_key}",
            )
            .when(callback, lambda q: (callback(q)))
        )

    def get_with_count_query(self, current_builder, callback):
        distant_table = self.distant_builder.get_table_name()
        intermediate_table = self.intermediary_builder.get_table_name()

        if not current_builder._columns:
            current_builder.select("*")

        return_query = current_builder.add_select(
            f"{self.attribute}_count",
            lambda q: (
                (
                    q.count("*")
                    .join(
                        f"{intermediate_table}",
                        f"{intermediate_table}.{self.foreign_key}",
                        "=",
                        f"{distant_table}.{self.other_owner_key}",
                    )
                    .where_column(
                        f"{intermediate_table}.{self.local_key}",
                        f"{current_builder.get_table_name()}.{self.local_owner_key}",
                    )
                    .table(distant_table)
                    .when(
                        callback,
                        lambda q: (
                            q.where_in(
                                self.foreign_key,
                                callback(
                                    self.distant_builder.select(self.other_owner_key)
                                ),
                            )
                        ),
                    )
                )
            ),
        )

        return return_query
