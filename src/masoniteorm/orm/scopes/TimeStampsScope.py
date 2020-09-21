from .BaseScope import BaseScope


class TimeStampsScope(BaseScope):
    """Global scope class to add soft deleting to models.
    """

    def on_boot(self, builder):
        print("booting soft deletes", builder)
        builder.set_global_scope("_timestamps", self.set_timestamp_create, action="insert")

    def on_remove(self, builder):
        pass

    def set_timestamp(owner_cls, query):
        owner_cls.updated_at = "now"

    def set_timestamp_create(self, builder):
        builder._creates.update({"updated_at": "now", "created_at": "now"})

