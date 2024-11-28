from .BaseRelationship import BaseRelationship
from ....collection import Collection

class HasMany(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, model_class, foreign_key=None, local_key=None, method=None):
        self.model_class = model_class
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.method = method
        self.owner = None

    def apply_query(self, builder, foreign_key_value=None, eager=None):
        owner = self.owner
        if not foreign_key_value:
            foreign_key_value = owner.__attributes__.get(self.local_key)
        if isinstance(foreign_key_value, Collection):
            foreign_key_value = foreign_key_value.serialize()
            return builder.where_in(self.local_key, foreign_key_value)
        return builder.where(self.local_key, foreign_key_value)

    def get_related(self, foreign, result, eager=None):
        if isinstance(result, Collection):
            print(self.foreign_key, result.pluck(self.local_key).serialize())
            foreign_key_value = result.pluck(self.local_key).serialize()
            print('fkk', result, foreign._model, self.foreign_key, self.local_key, foreign_key_value)
            result = foreign.where_in(self.foreign_key, foreign_key_value).get()
            result._related = self
            return result
        return self.apply_query(self.model_class, getattr(result, self.foreign_key)).get()

    def __call__(self, owner):
        """Fetch the related record when invoked."""
        related_model = self.model_class
        # print("related model", related_model)
        related_model.owner = self
        self.owner = owner
        foreign_key_value = owner.__attributes__.get(self.foreign_key)
        if not foreign_key_value:
            return self

        if self.method and self.method in owner._relationships:
            return owner._relationships[self.method]
        result = self.apply_query(related_model.builder).get()
        result._builder = self.apply_query(self.model_class.builder, foreign_key_value)
        result._related = self
        for item in result:
            item.__dict__['related'] = self
        return result

    def add_relation(self, model_instance, result, relation_key=None):
        # if result is a collection, do a where
        print("add relation", model_instance, relation_key, result.count())
        result = result or Collection()
        result._builder = self.model_class.builder
        result._related = self
        # print("add relation", model_instance, relation_key, result.count())
        return model_instance.add_relation({relation_key: result})

    def register_related(self, key, model, collection):
        print("register related", model, collection.serialize())
        model.add_relation({key: collection.get(getattr(model, self.local_key)) or Collection()})

    def relate_collection(self, key, result, collection):
        # print("relate collection", key, 'model', collection.where(self.foreign_key, getattr(record, self.local_key)).serialize())
        for record in result:
            print("relation", collection.where(self.foreign_key, getattr(record, self.local_key)).serialize())
            record.add_relation({key: collection.where(self.foreign_key, getattr(record, self.local_key)).first() or Collection()})
            # Articles
            print("relate collection inner", record)
        # return model.add_relation({key: collection.get(getattr(model, self.local_key)) or Collection()})
