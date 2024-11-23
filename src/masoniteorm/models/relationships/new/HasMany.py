class HasMany:
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
        print("getting has many")
        if self._related_instance is None:
            self._related_instance = self.apply_query().get()

        return self._related_instance

    def __call__(self):
        """
        Allow the relationship instance to be callable.
        """
        print("calling")
        return self.relationship.apply_query().get()
    

    def apply_query(self):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        print("applying query has many")
        return self.related_model.where(self.foreign_key, getattr(self.parent, self.foreign_key))

    def __getattr__(self, name, *args, **kwargs):
        """
        this is called when accesssing query builder methods on the relationship class

        this is returned when you do model.relationship().where(...)
        """
        

        try:
            return getattr(self.related_model, name)
        except AttributeError:
            pass

        related_instance = self.apply_query()

        if related_instance:
            return getattr(related_instance, name)
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")

    def __iter__(self):
        """
        This is called when iterating over the relationship class
        """
        print("iterating")
        return iter(self.apply_query().get())  # Use the iterator of the list