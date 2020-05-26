import json
import os
import unittest

import pendulum
import datetime

from app.User import User
from src.masonite.orm.collection import Collection
from src.masonite.orm.grammar.mssql_grammar import MSSQLGrammar
from src.masonite.orm.models import Model


class User(Model):
    def get_name(self):
        return f"Hello, {self.get_raw_attribute('name')}"


class TestAccessor(unittest.TestCase):
    def test_can_get_accessor(self):
        user = User.hydrate({"name": "joe", "email": "joe@masoniteproject.com"})
        self.assertEqual(user.email, "joe@masoniteproject.com")
        self.assertEqual(user.name, "Hello, joe")
