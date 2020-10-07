from unittest import TestCase
from src.masoniteorm.schema.grammars import SQLiteGrammar
from src.masoniteorm.schema.Blueprint import Blueprint

class TestSQLiteGrammar(TestCase):

    def test_grammar_can_columnize(self):
        
        blueprint = Blueprint(SQLiteGrammar)
        columns = (blueprint.string("name"), blueprint.string("age"))
        columnize = SQLiteGrammar().columnize(blueprint._columns)
        self.assertEqual(columnize, ['"name" VARCHAR NOT NULL', '"age" VARCHAR NOT NULL'])
        self.assertEqual(', '.join(columnize), '"name" VARCHAR NOT NULL, "age" VARCHAR NOT NULL')
        
        