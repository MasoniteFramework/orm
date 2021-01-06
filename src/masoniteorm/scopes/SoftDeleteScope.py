from .BaseScope import BaseScope


class SoftDeleteScope(BaseScope):
    """Global scope class to add soft deleting to models."""

    def on_boot(self, builder):
        builder.set_global_scope("_where_null", self._where_null, action="select")
        builder.set_global_scope(
            "_query_set_null_on_delete", self._query_set_null_on_delete, action="delete"
        )
        builder.macro("with_trashed", self._with_trashed)
        builder.macro("only_trashed", self._only_trashed)
        builder.macro("force_delete", self._force_delete)
        builder.macro("restore", self._restore)

    def on_remove(self, builder):
        builder.remove_global_scope("_where_null", action="select")
        builder.remove_global_scope("_query_set_null_on_delete", action="delete")

    def _where_null(self, builder):
        return builder.where_null("deleted_at")

    def _with_trashed(self, model, builder):
        builder.remove_global_scope("_where_null", action="select")
        return builder

    def _only_trashed(self, model, builder):
        builder.remove_global_scope("_where_null", action="select")
        return builder.where_not_null("deleted_at")

    def _force_delete(self, model, builder):
        return builder.remove_global_scope(self).set_action("delete")

    def _restore(self, model, builder):
        return builder.remove_global_scope(self).update({"deleted_at": None})

    def _query_set_null_on_delete(self, builder):
        return builder.set_action("update").set_updates(
            {"deleted_at": builder._model.get_new_datetime_string()}
        )
