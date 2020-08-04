import inspect
import unittest

from app.User import User
from src.masonite.orm.scopes import scope, SoftDeletes, TimeStamps
from src.masonite.orm.models import Model


class User(Model):
    __dry__ = True

    @scope
    def active(self, query, status):
        return query.where("active", status)

    @scope
    def gender(self, query, status):
        return query.where("gender", status)

class UserSoft(Model, SoftDeletes):
    __dry__ = True


class TestMySQLScopes(unittest.TestCase):
    def test_can_get_sql(self):
        sql = "SELECT * FROM `users` WHERE `users`.`name` = 'joe'"
        self.assertEqual(sql, User.where("name", "joe").to_sql())

    def test_active_scope(self):
        sql = "SELECT * FROM `users` WHERE `users`.`active` = '1' AND `users`.`name` = 'joe'"
        self.assertEqual(sql, User.active(1).where("name", "joe").to_sql())

    def test_active_scope_with_params(self):
        sql = "SELECT * FROM `users` WHERE `users`.`active` = '2' AND `users`.`name` = 'joe'"
        self.assertEqual(sql, User.active(2).where("name", "joe").to_sql())

    def test_can_chain_scopes(self):
        sql = "SELECT * FROM `users` WHERE `users`.`active` = '2' AND `users`.`gender` = 'W' AND `users`.`name` = 'joe'"
        self.assertEqual(sql, User.active(2).gender("W").where("name", "joe").to_sql())

    def test_can_use_global_scopes_on_select(self):
        sql = "SELECT * FROM `users` WHERE `users`.`name` = 'joe' AND `users`.`deleted_at` IS NOT NULL"
        self.assertEqual(
            sql, User.apply_scope(SoftDeletes).where("name", "joe").to_sql()
        )

    def test_can_use_global_scopes_on_select(self):
        sql = "SELECT * FROM `users` WHERE `users`.`name` = 'joe' AND `users`.`deleted_at` IS NOT NULL"
        self.assertEqual(
            sql, User.apply_scope(SoftDeletes).where("name", "joe").to_sql()
        )

    def test_can_use_global_scopes_on_delete(self):
        sql = "UPDATE `users` SET `users`.`deleted_at` = 'now' WHERE `users`.`name` = 'joe'"
        self.assertEqual(
            sql,
            User.apply_scope(SoftDeletes)
            .where("name", "joe")
            .delete(query=True)
            .to_sql(),
        )

    def test_can_use_global_scopes_on_time(self):
        sql = "INSERT INTO `users` (`users`.`name`, `users`.`updated_at`, `users`.`created_at`) VALUES ('Joe', 'now', 'now')"
        self.assertEqual(
            sql, User.apply_scope(TimeStamps).create({"name": "Joe"}, query=True)
        )

    def test_can_use_global_scopes_on_inherit(self):
        sql = "SELECT * FROM `user_softs` WHERE `user_softs`.`deleted_at` IS NOT NULL"
        self.assertEqual(
            sql, UserSoft.all(query=True)
        )
