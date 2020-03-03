from unittest import TestCase

class BaseTestCreateForeignKeyGrammar:

    def setUp(self):
        self.schema = Schema.on('mysql')

    def test_throw_exception_when_foreign_key_column_doesnt_exist(self):
        pass
    
    def test_throw_exception_when_columns_related_having_different_types(self):
        pass

    def test_throw_exception_when_foreign_key_table_doesnt_exist(self):
        pass

class TestMySQLForeignKeyGrammar(BaseTestCreateForeignKeyGrammar, TestCase):
    with self.schema.create('users') as table:
        table.increments('id')
        table.string('name')

        table.foreign('profile_id').references('user').on('users')

