import inspect
import unittest

from app.User import User
from src.masonite.orm.scopes import scope, SoftDeletes
from src.masonite.orm.models import Model


class TimeStamps:
    def boot_timestamps():
        return {
            "update": TimeStamps.set_timestamp,
            "insert": TimeStamps.set_timestamp_create,
        }

    def set_timestamp(owner_cls, query):
        owner_cls.updated_at = "now"

    def set_timestamp_create(owner_cls, query):
        owner_cls.builder.create(
            {"updated_at": "now", "created_at": "now",}
        )


class User(Model):
    @scope
    def active(query, status):
        return query.where("active", status)

    @scope
    def gender(query, status):
        return query.where("gender", status)


class TestMySQLScopes(unittest.TestCase):
    def test_can_get_sql(self):
        sql = "SELECT * FROM `users` WHERE `name` = 'joe'"
        self.assertEqual(sql, User.where("name", "joe").to_sql())

    def test_active_scope(self):
        sql = "SELECT * FROM `users` WHERE `active` = '1' AND `name` = 'joe'"
        self.assertEqual(sql, User.active(1).where("name", "joe").to_sql())

    def test_active_scope_with_params(self):
        sql = "SELECT * FROM `users` WHERE `active` = '2' AND `name` = 'joe'"
        self.assertEqual(sql, User.active(2).where("name", "joe").to_sql())

    def test_can_chain_scopes(self):
        sql = "SELECT * FROM `users` WHERE `active` = '2' AND `gender` = 'W' AND `name` = 'joe'"
        self.assertEqual(sql, User.active(2).gender("W").where("name", "joe").to_sql())

    def test_can_use_global_scopes_on_select(self):
        sql = "SELECT * FROM `users` WHERE `name` = 'joe' AND `deleted_at` IS NOT NULL"
        self.assertEqual(
            sql, User.apply_scope(SoftDeletes).where("name", "joe").to_sql()
        )

    def test_can_use_global_scopes_on_select(self):
        sql = "SELECT * FROM `users` WHERE `name` = 'joe' AND `deleted_at` IS NOT NULL"
        self.assertEqual(
            sql, User.apply_scope(SoftDeletes).where("name", "joe").to_sql()
        )

    def test_can_use_global_scopes_on_time(self):
        sql = "INSERT INTO `users` (`name`, `updated_at`, `created_at`) VALUES ('Joe', 'now', 'now')"
        self.assertEqual(sql, User.apply_scope(TimeStamps).create({"name": "Joe"}))
