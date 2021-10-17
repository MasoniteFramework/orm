class MySQLPostProcessor:
    """Post processor classes are responsable for modifying the result after a query.

    Post Processors are called after the connection calls the database in the
    Query Builder but before the result is returned in that builder method.

    We can use this oppurtunity to get things like the inserted ID.

    For the SQLite Post Processor we have an attribute on the connection class we can use to fetch the ID.
    """

    def process_insert_get_id(self, builder, results, id_key):
        """Process the results from the query to the database.

        Args:
            builder (masoniteorm.builder.QueryBuilder): The query builder class
            results (dict): The result from an insert query or the creates from the query builder.
            This is usually a dictionary.
            id_key (string): The key to set the primary key to. This is usually the primary key of the table.

        Returns:
            dictionary: Should return the modified dictionary.
        """

        if id_key not in results:
            results.update({id_key: builder._connection.get_cursor().lastrowid})
        return results
