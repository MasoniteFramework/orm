from .BaseRelationship import BaseRelationship
class HasOne(BaseRelationship):
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
        builder = builder.where(self.foreign_key, foreign_key_value).with_(eager or []).limit(1)
        return builder

    def get_related(self, foreign, result, eager=None):
        return self.apply_query(self.model_class, getattr(result, self.local_key)).first()

    def __call__(self, owner):
        """Return a query builder for the relationship."""
        related_model = self.model_class
        self.owner = owner
        
        # Get the foreign key value
        foreign_key_value = owner.__attributes__.get(self.local_key)
        if not foreign_key_value:
            return related_model.builder.where_raw("1 = 0")  # Return empty query if no foreign key
            
        # Return the query builder directly
        return self.apply_query(related_model.builder, foreign_key_value)

    def add_relation(self, model_instance, result, relation_key=None):
        return model_instance.add_relation({relation_key: result or None})
