import unittest
from src.masonite.orm.grammer.mssql_grammer import MSSQLGrammer
from app.User import User



class TestModel(unittest.TestCase):

    def test_can_call(self):
        print(User.find(1))
        print(User.find(2))
        print(User.find(3))
        print(User.find(4))
        print(User.find(5))
        print(User.find(6))
        print(User.find(7))
