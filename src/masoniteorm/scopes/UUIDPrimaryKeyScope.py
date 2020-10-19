import uuid
from .BaseScope import BaseScope


class UUIDPrimaryKeyScope(BaseScope):
    """Global scope class to use UUID4 as primary key."""

    def on_boot(self, builder):
        builder.set_global_scope(
            "_uuid", self.set_uuid_create, action="insert"
        )

    def on_remove(self, builder):
        pass

    def set_uuid_create(self, builder):
        builder._creates.update(
            {
                # TODO: later how to fetch uuid version here ?
                builder._model.__primary_key__: uuid.uuid4(),
            }
        )
