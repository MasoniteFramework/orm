class HasOne:
    def __init__(self, parent, related_model, foreign_key, local_key):
        self.parent = parent
        self.related_model = related_model
        self.foreign_key = foreign_key
        self.local_key = local_key
        self._related_instance = None

    def get(self):
        """
        Perform the database query to fetch the related model.
        """
        print("getting")
        if self._related_instance is None:
            self._related_instance = self.related_model.where(self.foreign_key, getattr(self.parent, self.foreign_key)).first()

        return self._related_instance

    def __call__(self):
        """
        Allow the relationship instance to be callable.
        """
        print("calling")
        return self
    
    def where(self, key, value):
        return self.related_model.where(key, value)