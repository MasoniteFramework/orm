from .TimeStampsScope import TimeStampsScope


class TimeStampsMixin:
    """Global scope class to add soft deleting to models."""

    def boot_TimeStampsMixin(self, builder):
        builder.set_global_scope(TimeStampsScope())

    def activate_timestamps(self, boolean=True):
        self.__timestamps__ = boolean
        return self
