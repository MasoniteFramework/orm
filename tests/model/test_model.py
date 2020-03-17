import unittest
from src.masonite.orm.grammar.mssql_grammar import MSSQLGrammar
from app.User import User
from src.masonite.orm.models.Model import Model
import os

if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class ProfileFillable(Model):
        __fillable__ = ['name']
        __table__ = 'profiles'

    class ProfileFillAsterisk(Model):
        __fillable__ = ['*']
        __table__ = 'profiles'

    class TestModel(unittest.TestCase):

        def test_can_use_fillable(self):
            sql = ProfileFillable.create({
                'name': 'Joe',
                'email': 'user@example.com'
            })

            self.assertEqual(
                sql, 
                "INSERT INTO `profiles` (`name`) VALUES ('Joe')"
            )

        def test_can_use_fillable_asterisk(self):
            sql = ProfileFillAsterisk.create({
                'name': 'Joe',
                'email': 'user@example.com'
            })

            self.assertEqual(
                sql, 
                "INSERT INTO `profiles` (`name`, `email`) VALUES ('Joe', 'user@example.com')"
            )
        # def test_can_call(self):
        #     print(User.find(1))
        #     print(User.find(2))
        #     print(User.find(3))
        #     print(User.find(4))
        #     print(User.find(5))
        #     print(User.find(6))
        #     print(User.find(7))
