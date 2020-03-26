class SoftDeletes:
    """Scope class to add soft deleting to models.
    """

    def boot_soft_delete():
        return {
            "select": SoftDeletes.query_where_null,
        }

    def query_where_null(owner_cls, query):
        return query.where_not_null("deleted_at")
