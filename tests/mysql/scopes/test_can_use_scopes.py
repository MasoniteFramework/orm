import inspect
import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import SoftDeletesMixin, scope
from tests.User import User


class User(Model):
    __dry__ = True

    @scope
    def active(self, query, status):
        return query.where("active", status)

    @scope
    def gender(self, query, status):
        return query.where("gender", status)


class UserSoft(Model, SoftDeletesMixin):
    __dry__ = True


class TestMySQLScopes(unittest.TestCase):
    def test_can_get_sql(self):
        sql = "SELECT * FROM `users` WHERE `users`.`name` = 'joe'"
        self.assertEqual(sql, User.where("name", "joe").to_sql())

    def test_active_scope(self):
        sql = "SELECT * FROM `users` WHERE `users`.`name` = 'joe' AND `users`.`active` = '1'"
        self.assertEqual(sql, User.where("name", "joe").active(1).to_sql())

    def test_active_scope_with_params(self):
        sql = "SELECT * FROM `users` WHERE `users`.`active` = '2' AND `users`.`name` = 'joe'"
        self.assertEqual(sql, User.active(2).where("name", "joe").to_sql())

    def test_can_chain_scopes(self):
        sql = "SELECT * FROM `users` WHERE `users`.`active` = '2' AND `users`.`gender` = 'W' AND `users`.`name` = 'joe'"
        self.assertEqual(sql, User.active(2).gender("W").where("name", "joe").to_sql())
