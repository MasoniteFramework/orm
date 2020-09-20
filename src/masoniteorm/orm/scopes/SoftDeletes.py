class SoftDeletes:
    """Global scope class to add soft deleting to models.
    """

    def boot(self, builder):
        return {
            "select": self.query_where_null,
            # "delete": self.query_set_null,
        }

    def query_where_null(self, builder):
        return query.where_null("deleted_at")

    # def query_set_null(self, builder):
    #     return query.set_action("update").set_updates({"deleted_at": "now"})
