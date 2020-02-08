import unittest
from src.masonite.orm.grammer.mssql_grammer import MSSQLGrammer
from app.User import User



class TestModel(unittest.TestCase):

    def test_can_call(self):
        print(User.find(1))
        print(User.find(1))
        print(User.find(1))
        print(User.find(1))
        print(User.find(1))
        print(User.find(1))
        print(User.find(1))
