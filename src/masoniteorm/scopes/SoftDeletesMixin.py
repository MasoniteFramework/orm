from .SoftDeleteScope import SoftDeleteScope


class SoftDeletesMixin:
    """Global scope class to add soft deleting to models."""

    def boot_SoftDeletesMixin(self, builder):
        builder.set_global_scope(SoftDeleteScope())
