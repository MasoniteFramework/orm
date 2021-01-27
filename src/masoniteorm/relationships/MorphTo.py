from .BaseRelationship import BaseRelationship
from ..collection import Collection


class MorphTo(BaseRelationship):

    _morph_map = {}

    def __init__(self, fn, morph_key="record_type", morph_id="record_id"):
        if isinstance(fn, str):
            self.morph_key = fn
            self.morph_id = morph_key
        else:
            self.fn = fn
            self.morph_id = morph_id

    def get_builder(self):
        return self._related_builder

    def __get__(self, instance, owner):
        """This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """

        self._related_builder = instance.builder

        if instance.is_loaded():
            if self.morph_key in instance._relationships:
                return instance._relationships[self.morph_key]

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

        # return

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
        raise NotImplementedError

    def register_related(self, key, model, collection):
        raise NotImplementedError

    def morph_map(self):
        return self._morph_map

    @classmethod
    def set_morph_map(cls, morph_map):
        cls._morph_map = morph_map
        return cls
