class MSSQLPostProcessor:
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

        last_id = builder.new_connection().query(
            f"SELECT @@Identity as [id]", results=1
        )

        id = last_id["id"]

        if str(id).isdigit():
            id = int(id)
        else:
            id = str(id)

        results.update({id_key: id})
        return results
