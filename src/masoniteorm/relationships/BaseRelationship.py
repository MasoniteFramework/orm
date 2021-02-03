from ..collection.Collection import Collection


class BaseRelationship:
    def __init__(self, fn, local_key=None, foreign_key=None):
        if isinstance(fn, str):
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
        """This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """
        attribute = self.fn.__name__
        relationship = self.fn(self)()

        self._related_builder = relationship.builder

        if instance.is_loaded():
            if attribute in instance._relationships:
                return instance._relationships[attribute]

            result = self.apply_query(self._related_builder, instance)
            return result
        else:
            return self

    def __getattr__(self, attribute):
        relationship = self.fn(self)()
        return getattr(relationship.builder, attribute)

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
