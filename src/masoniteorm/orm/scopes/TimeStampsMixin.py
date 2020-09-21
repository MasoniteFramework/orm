from .TimeStampsScope import TimeStampsScope


class TimeStampsMixin:
    """Global scope class to add soft deleting to models.
    """

    def boot_TimeStampsMixin(self, builder):
        print("bb", builder)
        builder.set_global_scope(TimeStampsScope())
