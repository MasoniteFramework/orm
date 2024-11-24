class BaseRelationship:
    def init(self, model_class, local_key=None, foreign_key=None):
        self.model_class = model_class
        self.local_key = local_key
        self.foreign_key = foreign_key

    def __call__(self, owner):
        """Create and return the relationship query."""
        related_model = self.model_class()
        return self.apply_query(related_model.builder, owner)
