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
        self.set_keys(instance, attribute)
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

    def get_where_exists_query(self, builder, callback):
        query = self.get_builder()
        builder.where_exists(
            callback(
                query.where_column(
                    f"{query.get_table_name()}.{self.foreign_key}",
                    f"{builder.get_table_name()}.{self.local_key}",
                )
            )
        )
        return query

    def get_with_count_query(self, builder, callback):
        query = self.get_builder()
        if not builder._columns:
            builder = builder.select("*")

        return_query = builder.add_select(
            f"{query.get_table_name()}_count",
            lambda q: (
                (
                    q.count("*")
                    .where_column(
                        f"{builder.get_table_name()}.{self.local_key}",
                        f"{query.get_table_name()}.{self.foreign_key}",
                    )
                    .table(query.get_table_name())
                    .when(
                        callback,
                        lambda q: (
                            q.where_in(
                                builder._model.get_primary_key(),
                                callback(
                                    query.select(builder._model.get_primary_key())
                                ),
                            )
                        ),
                    )
                )
            ),
        )

        return return_query

    def attach(self, current_model, related_record):
        return current_model.update(
            {self.local_key: getattr(related_record, self.foreign_key)}
        )

    def detach(self, current_model, related_record):
        return current_model.where(
            {self.local_key: getattr(related_record, self.foreign_key)}
        ).delete()

    def attach_related(self, current_model, related_record):
        return related_record.update(
            {self.foreign_key: getattr(current_model, self.local_key)}
        )

    def detach_related(self, current_model, related_record):
        return related_record.where(
            {self.foreign_key: getattr(current_model, self.local_key)}
        ).delete()

    def query_has(self, current_query_builder):
        related_builder = self.get_builder()

        current_query_builder.where_exists(
            related_builder.where_column(
                f"{related_builder.get_table_name()}.{self.foreign_key}",
                f"{current_query_builder.get_table_name()}.{self.local_key}",
            )
        )

        return related_builder
