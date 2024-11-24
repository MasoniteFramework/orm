from .BaseRelationship import BaseRelationship
class HasOne(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, model_class, foreign_key=None, local_key=None):
        self.model_class = model_class
        self.foreign_key = foreign_key
        self.local_key = local_key
        self.owner = None

    def apply_query(self, builder, foreign_key_value=None):
        owner = self.owner
        if not foreign_key_value:
            foreign_key_value = owner.__attributes__.get(self.local_key)
        builder = builder.where(self.foreign_key, foreign_key_value)
        return builder

    def get_related(self, foreign, result):
        return self.apply_query(self.model_class, getattr(result, self.local_key)).first()


    def __call__(self, owner):
        """Fetch the related record when invoked."""
        related_model = self.model_class
        print(f"Method called: {method_name}")
        related_model.owner = self
        self.owner = owner
        foreign_key_value = owner.__attributes__.get(self.local_key)
        if not foreign_key_value:
            print("No foreign key value")
            return self
        print("Fetching has one", owner.__relationships__)
        builder = self.apply_query(related_model.builder)
        result = builder.first()
        self.owner = owner
        result.__dict__['related'] = self
        return result

