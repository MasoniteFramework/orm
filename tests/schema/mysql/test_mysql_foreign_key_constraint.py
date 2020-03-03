from src.masonite.orm.schema.Schema import Schema
from unittest import TestCase

class BaseTestCreateForeignKeyGrammar(TestCase):

    def setUp(self):
        self.schema = Schema.on('mysql')

    def test_quantity_of_relations(self):
        with self.schema.create('users') as table:
            table.foreign('user_id').references('id').on('users')
            table.foreign('profile_id').references('id').on('profile')
            table.foreign('company_id').references('id').on('company')

        self.assertEqual(len(table._relations), 3)

    def test_correct_data_of_foreign_key_when_defined_more_than_one_relation(self):
        with self.schema.create('users') as table:
            table.foreign('user_id').references('id').on('users')
            table.foreign('profile_id').references('id').on('profile')

        first_relation = table._relations[0]
        second_relation = table._relations[1]

        self.assertEqual(first_relation.get("local_column"), "user_id")
        self.assertEqual(first_relation.get("external_column"), "id")
        self.assertEqual(first_relation.get("table"), "users")

        self.assertEqual(second_relation.get("local_column"), "profile_id")
        self.assertEqual(second_relation.get("external_column"), "id")
        self.assertEqual(second_relation.get("table"), "profile")

    def test_throw_exception_when_foreign_key_column_doesnt_exist(self):
        pass
    
    def test_throw_exception_when_columns_related_having_different_types(self):
        pass

    def test_throw_exception_when_foreign_key_table_doesnt_exist(self):
        pass

# class TestMySQLForeignKeyGrammar(BaseTestCreateForeignKeyGrammar):
#     with self.schema.create('users') as table:
#         table.increments('id')
#         table.string('name')

#         table.foreign('profile_id').references('user').on('users')

