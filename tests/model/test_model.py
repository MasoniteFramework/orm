import unittest
from src.masonite.orm.grammar.mssql_grammar import MSSQLGrammar
from app.User import User
import os

if os.getenv('RUN_MYSQL_DATABASE', False) == 'True':
    class TestModel(unittest.TestCase):

        def test_can_call(self):
            print(User.find(1))
            print(User.find(2))
            print(User.find(3))
            print(User.find(4))
            print(User.find(5))
            print(User.find(6))
            print(User.find(7))
