class PostgresPostProcessor:
    """Post processor classes are responsable for modifying the result after a query.

    Post Processors are called after the connection calls the database in the
    Query Builder but before the result is returned in that builder method.

    We can use this oppurtunity to get things like the inserted ID.

    For the Postgres Post Processor we have a RETURNING * string in the insert so the result
    will already have the full inserted record in the results. Therefore, we can just return
    the results
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

        return results

    def get_column_value(self, builder, column, results, id_key, id_value):
        """Gets the specific column value from a table. Typically done after an update to
        refetch the new value of a field.

            builder (masoniteorm.builder.QueryBuilder): The query builder class
            column (string): The column to refetch the value for.
            results (dict): The result from an update query from the query builder.
            This is usually a dictionary.
            id_key (string): The key to fetch the primary key for. This is usually the primary key of the table.
            id_value (string): The value of the primary key to fetch
        """

        if column in results:
            return results[column]

        new_builder = builder.select(column)
        if id_key and id_value:
            new_builder.where(id_key, id_value)
            return new_builder.first()[column]

        return {}
