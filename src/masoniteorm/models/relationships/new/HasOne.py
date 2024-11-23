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
        if self._related_instance is None:
            self._related_instance = self.apply_query().first()

        return self._related_instance

    def __call__(self):
        """
        Allow the relationship instance to be callable.
        """
        return self
    
    def __repr__(self):
        return repr(self.related_model)
    
    def where(self, key):
        return self.related_model.where(key, value)

    def apply_query(self):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """

        return self.related_model.where(self.foreign_key, getattr(self.parent, self.foreign_key))