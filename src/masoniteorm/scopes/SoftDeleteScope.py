from .BaseScope import BaseScope


class SoftDeleteScope(BaseScope):
    """Global scope class to add soft deleting to models."""

    def on_boot(self, builder):
        builder.set_global_scope("_where_null", self._where_null, action="select")
        builder.set_global_scope(
            "_query_set_null_on_delete", self._query_set_null_on_delete, action="delete"
        )
        builder.macro("with_trashed", self._with_trashed)

    def on_remove(self, builder):
        builder.remove_global_scope("_where_null", action="select")

    def _where_null(self, builder):
        return builder.where_null("deleted_at")

    def _with_trashed(self, model, builder):
        builder.remove_global_scope("_where_null", action="select")
        return builder

    def _query_set_null_on_delete(self, builder):
        return builder.set_action("update").set_updates(
            {"deleted_at": builder._model.get_new_datetime_string()}
        )
