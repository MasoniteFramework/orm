import uuid
from .BaseScope import BaseScope


class UUIDPrimaryKeyScope(BaseScope):
    """Global scope class to use UUID4 as primary key."""

    def on_boot(self, builder):
        builder.set_global_scope(
            "_UUID_primary_key", self.set_uuid_create, action="insert"
        )

    def on_remove(self, builder):
        pass

    def generate_uuid(self, builder, uuid_version):
        # UUID 3 and 5 requires parameters
        uuid_func = getattr(uuid, f"uuid{uuid_version}")
        args = []
        if uuid_version in [3, 5]:
            args = [builder._model.__uuid_namespace__, builder._model.__uuid_name__]

        return str(uuid_func(*args))

    def set_uuid_create(self, builder):
        # if there is already a primary key, no need to set a new one
        if builder._model.__primary_key__ not in builder._creates:
            uuid_version = getattr(builder._model, "__uuid_version__", 4)
            builder._creates.update(
                {
                    builder._model.__primary_key__: self.generate_uuid(
                        builder, uuid_version
                    )
                }
            )
