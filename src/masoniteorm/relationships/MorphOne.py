from ..collection import Collection
from ..config import load_config
from .BaseRelationship import BaseRelationship


class MorphOne(BaseRelationship):
    def __init__(self, fn, morph_key="record_type", morph_id="record_id"):
        if isinstance(fn, str):
            self.fn = None
            self.morph_key = fn
            self.morph_id = morph_key
        else:
            self.fn = fn
            self.morph_id = morph_id
            self.morph_key = morph_key

    def get_builder(self):
        return self._related_builder

    def set_keys(self, owner, attribute):
        self.morph_id = self.morph_id or "record_id"
        self.morph_key = self.morph_key or "record_type"
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
        self._related_builder = instance.builder
        self.polymorphic_builder = self.fn(self)()
        self.set_keys(owner, self.fn)

        if instance.is_loaded():
            if attribute in instance._relationships:
                return instance._relationships[attribute]

            result = self.apply_query(self._related_builder, instance)

            return result
        else:
            return self

    def __getattr__(self, attribute):
        relationship = self.fn(self)()
        return getattr(relationship.builder, attribute)

    def apply_query(self, builder, instance):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            builder {oject} -- The relationship object
            instance {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        polymorphic_key = self.get_record_key_lookup(builder._model)
        polymorphic_builder = self.polymorphic_builder

        return (
            polymorphic_builder.where(self.morph_key, polymorphic_key)
            .where(self.morph_id, instance.get_primary_key_value())
            .first()
        )

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

        if isinstance(relation, Collection):
            record_type = self.get_record_key_lookup(relation.first())
            if callback:
                return callback(
                    self.polymorphic_builder.where(
                        f"{self.polymorphic_builder.get_table_name()}.{self.morph_key}",
                        record_type,
                    ).where_in(
                        self.morph_id,
                        relation.pluck(
                            relation.first().get_primary_key(), keep_nulls=False
                        ).unique(),
                    )
                ).get()

            return (
                self.polymorphic_builder.where(
                    f"{self.polymorphic_builder.get_table_name()}.{self.morph_key}",
                    record_type,
                )
                .where_in(
                    self.morph_id,
                    relation.pluck(
                        relation.first().get_primary_key(), keep_nulls=False
                    ).unique(),
                )
                .get()
            )

        else:
            record_type = self.get_record_key_lookup(relation)
            if callback:
                return callback(
                    self.polymorphic_builder.where(self.morph_key, record_type).where(
                        self.morph_id, relation.get_primary_key_value()
                    )
                ).first()

            return (
                self.polymorphic_builder.where(self.morph_key, record_type)
                .where(self.morph_id, relation.get_primary_key_value())
                .first()
            )

    def register_related(self, key, model, collection):
        record_type = self.get_record_key_lookup(model)
        related = (
            collection.where(self.morph_key, record_type)
            .where(self.morph_id, model.get_primary_key_value())
            .first()
        )

        model.add_relation({key: related})

    def morph_map(self):
        return load_config().DB._morph_map

    def get_record_key_lookup(self, relation):
        record_type = None
        for record_type_loop, model in self.morph_map().items():
            if model == relation.__class__:
                record_type = record_type_loop
                break

        if not record_type:
            raise ValueError(
                f"Could not find the record type key for the {relation} class"
            )

        return record_type

    def attach(self, current_model, related_record):
        raise NotImplementedError(
            "HasOneThrough relationship does not implement the attach method"
        )

    def attach_related(self, current_model, related_record):
        raise NotImplementedError(
            "HasOneThrough relationship does not implement the attach_related method"
        )

    def relate(self, related_record):
        raise NotImplementedError(
            "MorphOne relationship does not implement the relate method"
        )

    def query_has(self, related_record, method="where_exists"):
        raise NotImplementedError(
            "MorphOne relationship does not implement the has method"
        )

    def query_where_exists(self, related_record, method="where_exists"):
        raise NotImplementedError(
            "MorphOne relationship does not implement the where_exists method"
        )
