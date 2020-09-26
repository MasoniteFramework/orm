class MySQLProcessor:
    def process_insert_get_id(self, builder, results, id_key):

        results.update({id_key: builder.get_connection().get_cursor().lastrowid})
        return results
