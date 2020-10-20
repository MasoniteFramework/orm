from .UUIDPrimaryKeyScope import UUIDPrimaryKeyScope


class UUIDPrimaryKeyMixin:
    """Global scope class to add UUID as primary key to models."""

    def boot_UUIDPrimaryKeyMixin(self, builder):
        builder.set_global_scope(UUIDPrimaryKeyScope())
