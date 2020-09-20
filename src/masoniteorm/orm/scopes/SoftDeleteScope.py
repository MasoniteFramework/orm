from .BaseScope import BaseScope


class SoftDeleteScope(BaseScope):
    """Global scope class to add soft deleting to models.
    """

    def boot(self, builder):
        builder.set_scope("query_where_null", self.query_where_null)
        builder.macro("with_trashed", self._with_trashed)

    def on_remove(self, builder):
        pass

    def query_where_null(self, builder):
        return builder.where_null("deleted_at")

    def _with_trashed(self, model, builder):
        builder.remove_global_scope("query_where_null")
        return builder

    # def query_set_null(self, builder):
    #     return query.set_action("update").set_updates({"deleted_at": "now"})
