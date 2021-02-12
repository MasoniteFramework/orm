from .SoftDeleteScope import SoftDeleteScope


class SoftDeletesMixin:
    """Global scope class to add soft deleting to models."""

    __deleted_at__ = "deleted_at"

    def boot_SoftDeletesMixin(self, builder):
        builder.set_global_scope(SoftDeleteScope(self.__deleted_at__))

    def get_deleted_at_column(self):
        return self.__deleted_at__
