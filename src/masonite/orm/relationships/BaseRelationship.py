from ..collection.Collection import Collection


class BaseRelationship:
    def __init__(self, fn, local_key=None, foreign_key=None):
        if isinstance(fn, str):
            self.local_key = fn
            self.foreign_key = local_key
        else:
            self.fn = fn
            self.foreign_key = foreign_key

    def __set_name__(self, cls, name):
        """This method is called right after the decorator is registered.

        At this point we finally have access to the model cls

        Arguments:
            name {object} -- The model class.
        """
        self.cls = cls

    def __call__(self, fn=None, *args, **kwargs):
        """This method is called when the decorator contains arguments.

        When you do something like this:

        @belongs_to('id', 'user_id').

        In this case, the {fn} argument will be the callable.
        """
        if callable(fn):
            self.fn = fn

        return self

    def __get__(self, instance, owner):
        """This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """
        relationship = self.fn(self)
        if not instance:
            """This means the user called the attribute rather than accessed it.
            In this case we want to return the builder
            """
            self.relationship = self.fn(self)
            self.relationship.boot()
            return self.relationship.builder

        """After we access the result and we wanted to load it we will fetch the loaded result
        """
        if self.fn.__name__ in instance._loaded_relationships:
            return instance._loaded_relationships[self.fn.__name__]

        """Since the attribute is accessed we want the relationship hydrated and ready to go.
        """
        query_data = self.apply_query(
            relationship, instance, self.foreign_key, self.local_key
        )

        if isinstance(query_data, dict):
            loaded_result = relationship.hydrate(query_data)
            if self.fn.__name__ in owner._loads:
                instance._loaded_relationships[self.fn.__name__] = loaded_result
            return loaded_result
        elif isinstance(query_data, list):
            results = []
            for result in query_data:
                results.append(relationship.hydrate(result))
            loaded_result = relationship.new_collection(results)
            if self.fn.__name__ in owner._loads:
                instance._loaded_relationships[self.fn.__name__] = loaded_result
            return loaded_result

        raise Exception("found", query_data)

    def apply_query(self, foreign, owner, foreign_key, local_key):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.
            foreign_key {string} -- The column to access on the relationship model.
            local_key {string} -- The column to access on the current model.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """

        return foreign.where(foreign_key, owner().__attributes__[local_key]).first()
