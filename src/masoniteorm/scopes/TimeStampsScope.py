from ..expressions.expressions import UpdateQueryExpression
from .BaseScope import BaseScope


class TimeStampsScope(BaseScope):
    """Global scope class to add soft deleting to models."""

    def on_boot(self, builder):
        builder.set_global_scope(
            "_timestamps", self.set_timestamp_create, action="insert"
        )

        builder.set_global_scope(
            "_timestamp_update", self.set_timestamp_update, action="update"
        )

    def on_remove(self, builder):
        pass

    def set_timestamp(owner_cls, query):
        owner_cls.updated_at = "now"

    def set_timestamp_create(self, builder):
        if not builder._model.__timestamps__:
            return builder

        builder._creates.update(
            {
                builder._model.date_updated_at: builder._model.get_new_date().to_datetime_string(),
                builder._model.date_created_at: builder._model.get_new_date().to_datetime_string(),
            }
        )

    def set_timestamp_update(self, builder):
        if not builder._model.__timestamps__:
            return builder

        for update in builder._updates:
            if builder._model.date_updated_at in update.column:
                return
        builder._updates += (
            UpdateQueryExpression(
                {
                    builder._model.date_updated_at: builder._model.get_new_date().to_datetime_string()
                }
            ),
        )
