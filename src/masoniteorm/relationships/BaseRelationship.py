class BaseRelationship:
    def __init__(self, fn, local_key=None, foreign_key=None):
        if isinstance(fn, str):
            self.fn = None
            self.local_key = fn
            self.foreign_key = local_key
        else:
            self.fn = fn
            self.local_key = local_key
            self.foreign_key = foreign_key

    def __set_name__(self, cls, name):
        """This method is called right after the decorator is registered.

        At this point we finally have access to the model cls

        Arguments:
            name {object} -- The model class.
        """
        pass

    def __call__(self, fn=None, *args, **kwargs):
        """This method is called when the decorator contains arguments.

        When you do something like this:

        @belongs_to('id', 'user_id').

        In this case, the {fn} argument will be the callable.
        """
        if callable(fn):
            self.fn = fn

        return self

    def get_builder(self):
        return self._related_builder

    def __get__(self, instance, owner):
        """
        This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """
        attribute = self.fn.__name__
        relationship = self.fn(instance)()
        self.set_keys(instance, attribute)
        self._related_builder = relationship.builder

        if not instance.is_loaded():
            return self

        if attribute in instance._relationships:
            return instance._relationships[attribute]

        return self.apply_query(self._related_builder, instance)

    def __getattr__(self, attribute):
        relationship = self.fn(self)()
        return getattr(relationship.builder, attribute)

    def apply_query(self, foreign, owner):
        """Return a dictionary to hydrate the model with

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'apply_query' method"
        )

    def query_where_exists(self, builder, callback, method="where_exists"):
        """Adds a criteria clause to the query filter for existing related records"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'query_where_exists' method"
        )

    def joins(self, builder, clause=None):
        """Helper method for adding join clauses to a relationship"""
        other_table = self.get_builder().get_table_name()
        local_table = builder.get_table_name()
        return builder.join(
            other_table,
            f"{local_table}.{self.local_key}",
            "=",
            f"{other_table}.{self.foreign_key}",
            clause=clause,
        )

    def get_with_count_query(self, builder, callback):
        """Adds a clause to the query to get the record count of the relationship"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'get_with_count_query' method"
        )

    def attach(self, current_model, related_record):
        """Link a related model to the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'attach' method"
        )

    def get_related(self, query, relation, eagers=None, callback=None):
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'get_related' method"
        )

    def relate(self, related_record):
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'relate' method"
        )

    def detach(self, current_model, related_record):
        """Unlink a related model from the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'detach' method"
        )

    def attach_related(self, current_model, related_record):
        """Unlink a related model from the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'attach_related' method"
        )

    def detach_related(self, current_model, related_record):
        """Unlink a related model from the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'detach_related' method"
        )

    def query_has(self, current_query_builder, method="where_exists"):
        """Adds a clause to the query to chek if a rwlarion exists"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'query_has' method"
        )

    def map_related(self, related_result):
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'related_result' method"
        )
