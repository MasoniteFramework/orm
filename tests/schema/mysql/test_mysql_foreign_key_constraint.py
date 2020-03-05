from src.masonite.orm.schema.Schema import Schema
from src.masonite.orm.schema.constraints.constraints import ForeignKeyConstraint
from unittest import TestCase

class BaseTestCreateForeignKeyGrammar(TestCase):

    def setUp(self):
        self.schema = Schema.on('mysql')
        self.table = None

        with self.schema.create('users') as self.table:
            self.table.foreign('user_id').references('id').on('users')
            self.table.foreign('profile_id').references('id').on('profile')
            self.table.foreign('company_id').references('id').on('company')

    def test_quantity_of_relations(self):
        self.assertEqual(len(self.table._constraints), 3)

    def test_correct_type_returned_by_foreign_relation(self):
        first_relation = self.table._constraints[0]
        self.assertIsInstance(first_relation, ForeignKeyConstraint)

    def test_correct_data_of_foreign_key_when_defined_more_than_one_relation(self):
        pass

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

