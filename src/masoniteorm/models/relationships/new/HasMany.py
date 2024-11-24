from .BaseRelationship import BaseRelationship

class HasMany(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, model_class, foreign_key=None, local_key=None):
        self.model_class = model_class
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.owner = None

    def apply_query(self, builder):
        owner = self.owner
        foreign_key_value = owner.__attributes__.get(self.foreign_key)
        return builder.where(self.local_key, foreign_key_value)


    def __call__(self, owner):
        """Fetch the related record when invoked."""
        related_model = self.model_class
        # print("related model", related_model)
        related_model.owner = self
        self.owner = owner
        foreign_key_value = owner.__attributes__.get(self.foreign_key)
        if not foreign_key_value:
            return None
        # builder = related_model.builder.where(self.local_key, foreign_key_value)
        builder = self.apply_query(related_model.builder)
        result = builder.get()
        for item in result:
            item.__dict__['related'] = self
        self.owner = owner
        return result

