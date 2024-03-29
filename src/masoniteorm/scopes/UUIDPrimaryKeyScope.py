import uuid

from .BaseScope import BaseScope


class UUIDPrimaryKeyScope(BaseScope):
    """Global scope class to use UUID4 as primary key."""

    def on_boot(self, builder):
        builder.set_global_scope(
            "_UUID_primary_key", self.set_uuid_create, action="insert"
        )
        builder.set_global_scope(
            "_UUID_primary_key", self.set_bulk_uuid_create, action="bulk_create"
        )

    def on_remove(self, builder):
        pass

    def generate_uuid(self, builder, uuid_version, bytes=False):
        # UUID 3 and 5 requires parameters
        uuid_func = getattr(uuid, f"uuid{uuid_version}")
        args = []
        if uuid_version in [3, 5]:
            args = [builder._model.__uuid_namespace__, builder._model.__uuid_name__]

        return uuid_func(*args).bytes if bytes else str(uuid_func(*args))

    def build_uuid_pk(self, builder):
        uuid_version = getattr(builder._model, "__uuid_version__", 4)
        uuid_bytes = getattr(builder._model, "__uuid_bytes__", False)
        return {
            builder._model.__primary_key__: self.generate_uuid(
                builder, uuid_version, uuid_bytes
            )
        }

    def set_uuid_create(self, builder):
        # if there is already a primary key, no need to set a new one
        if builder._model.__primary_key__ not in builder._creates:
            builder._creates.update(self.build_uuid_pk(builder))

    def set_bulk_uuid_create(self, builder):
        for idx, create_atts in enumerate(builder._creates):
            if builder._model.__primary_key__ not in create_atts:
                builder._creates[idx].update(self.build_uuid_pk(builder))
