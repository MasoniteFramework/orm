from .BaseRelationship import BaseRelationship
from ..collection import Collection


class BelongsTo(BaseRelationship):
    """Belongs To Relationship Class.
    """

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
        # pass
        return foreign.where(foreign_key, owner.__attributes__[local_key]).first()

    def get_related(self, relation):
        """Gets the relation needed between the relation and the related builder. If the relation is a collection
        then will need to pluck out all the keys from the collection and fetch from the related builder. If 
        relation is just a Model then we can just call the model based on the value of the related 
        builders primary key.

        Args:
            relation (Model|Collection):

        Returns:
            Model|Collection
        """        
        builder = self.get_builder()
        if isinstance(relation, Collection):
            return builder.where_in(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.pluck(self.local_key),
            ).first()
        else:
            return builder.where(
                f"{builder.get_table_name()}.{self.foreign_key}",
                relation.get_primary_key_value(),
            ).first()
