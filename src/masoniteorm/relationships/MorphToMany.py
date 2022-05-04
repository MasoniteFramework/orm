from ..collection import Collection
from .BaseRelationship import BaseRelationship
from ..config import load_config


class MorphToMany(BaseRelationship):
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
        model = self.morph_map().get(instance.__attributes__[self.morph_key])
        record = instance.__attributes__[self.morph_id]

        return model.where(model.get_primary_key(), record).first()

    def get_related(self, query, relation, eagers=None):
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
            relations = Collection()
            for group, items in relation.group_by(self.morph_key).items():
                morphed_model = self.morph_map().get(group)
                relations.merge(
                    morphed_model.where_in(
                        f"{morphed_model.get_table_name()}.{morphed_model.get_primary_key()}",
                        Collection(items)
                        .pluck(self.morph_id, keep_nulls=False)
                        .unique(),
                    ).get()
                )
            return relations
        else:
            model = self.morph_map().get(getattr(relation, self.morph_key))
            if model:
                return model.find([getattr(relation, self.morph_id)])

    def register_related(self, key, model, collection):
        morphed_model = self.morph_map().get(getattr(model, self.morph_key))

        related = collection.where(
            morphed_model.get_primary_key(), getattr(model, self.morph_id)
        )

        model.add_relation({key: related})

    def morph_map(self):
        return load_config().DB._morph_map

    def attach(self, current_model, related_record):
        raise NotImplementedError(
            "MorphToMany relationship does not implement the attach method"
        )

    def attach_related(self, current_model, related_record):
        raise NotImplementedError(
            "MorphToMany relationship does not implement the attach_related method"
        )
