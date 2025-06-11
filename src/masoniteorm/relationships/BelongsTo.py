from ..collection import Collection
from .BaseRelationship import BaseRelationship


class BelongsTo(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, fn, local_key=None, foreign_key=None):
        if isinstance(fn, str):
            self.fn = None
            self.local_key = fn or "id"
            self.foreign_key = local_key
        else:
            self.fn = fn
            self.local_key = local_key or "id"
            self.foreign_key = foreign_key

    def set_keys(self, owner, attribute):
        self.local_key = self.local_key or f"{attribute}_id"
        self.foreign_key = self.foreign_key or "id"
        return self

    def apply_query(self, foreign, owner):
        """Apply the query and return a dictionary to be hydrated

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        return foreign.where(
            self.foreign_key, owner.__attributes__[self.local_key]
        ).first()

    def query_has(self, current_query_builder, method="where_exists"):
        related_builder = self.get_builder()

        getattr(current_query_builder, method)(
            related_builder.where_column(
                f"{related_builder.get_table_name()}.{self.foreign_key}",
                f"{current_query_builder.get_table_name()}.{self.local_key}",
            )
        )

        return related_builder

    def query_where_exists(self, builder, callback, method="where_exists"):
        query = self.get_builder()
        getattr(builder, method)(
            callback(
                query.where_column(
                    f"{query.get_table_name()}.{self.foreign_key}",
                    f"{builder.get_table_name()}.{self.local_key}",
                )
            )
        )
        return query

    def get_related(self, query, relation, eagers=(), callback=None):
        """Gets the relation needed between the relation and the related builder. If the relation is a collection
        then will need to pluck out all the keys from the collection and fetch from the related builder. If
        relation is just a Model then we can just call the model based on the value of the related
        builders primary key.

        Args:
            relation (Model|Collection):

        Returns:
            Model|Collection
        """
        builder = self.get_builder().with_(eagers)
        if callback:
            callback(builder)

        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                Collection(relation._get_value(self.local_key)).unique(),
            ).get()

        else:
            return builder.where(
                f"{builder.get_table_name()}.{self.foreign_key}",
                getattr(relation, self.local_key),
            ).first()

    def register_related(self, key, model, collection):
        related = collection.get(getattr(model, self.local_key), None)

        model.add_relation({key: related[0] if related else None})

    def map_related(self, related_result):
        return related_result.group_by(self.foreign_key)

    def attach(self, current_model, related_record):
        foreign_key_value = getattr(related_record, self.foreign_key)
        if not current_model.is_created():
            current_model.fill({self.local_key: foreign_key_value})
            return current_model.create(
                current_model.all_attributes(), cast=True
            )

        current_model.update({self.local_key: foreign_key_value})
        return current_model

    def detach(self, current_model, related_record):
        return current_model.update({self.local_key: None})

    def relate(self, related_record):
        return (
            self.get_builder()
            .where(
                self.foreign_key, related_record.__attributes__[self.local_key]
            )
            ._set_creates_related(
                {
                    self.foreign_key: related_record.__attributes__[
                        self.local_key
                    ]
                }
            )
        )
