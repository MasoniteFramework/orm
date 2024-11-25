from .BaseRelationship import BaseRelationship

class HasMany(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, model_class, foreign_key=None, local_key=None):
        self.model_class = model_class
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.owner = None

    def apply_query(self, builder, foreign_key_value=None, eager=None):
        
        owner = self.owner
        foreign_key_value = owner.__attributes__.get(self.foreign_key)
        return builder.where(self.local_key, foreign_key_value)

    def get_related(self, foreign, result, eager=None):
        return self.apply_query(self.model_class, getattr(result, self.foreign_key)).first()

    def __call__(self, owner):
        """Fetch the related record when invoked."""
        related_model = self.model_class
        # print("related model", related_model)
        related_model.owner = self
        self.owner = owner
        foreign_key_value = owner.__attributes__.get(self.foreign_key)
        if not foreign_key_value:
            return self
        builder = self.apply_query(related_model.builder)
        result = builder.get()
        for item in result:
            item.__dict__['related'] = self
        return result

    def add_relation(self, model_instance, result, relation_key=None):
        # if result is a collection, do a where
       return model_instance.add_relation({relation_key: result or []})