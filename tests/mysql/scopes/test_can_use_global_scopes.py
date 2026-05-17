import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import (
    SoftDeletesMixin,
)


class UserSoft(Model, SoftDeletesMixin):
    __dry__ = True


class User(Model):
    __dry__ = True


class TestMySQLGlobalScopes(unittest.TestCase):
    def test_can_use_global_scopes_on_select(self):
        expected_sql = "SELECT * FROM `user_softs` WHERE `user_softs`.`name` = 'joe' AND `user_softs`.`deleted_at` IS NULL"
        query_sql = UserSoft.where("name", "joe").to_sql()
        self.assertEqual(query_sql, expected_sql)

    # def test_can_use_global_scopes_on_delete(self):
    #     expected_sql = "UPDATE `users` SET `users`.`deleted_at` = 'now' WHERE `users`.`name` = 'joe'"
    #     self.assertEqual(
    #         expected_sql,
    #         User.apply_scope(SoftDeletes)
    #         .where("name", "joe")
    #         .delete(query=True)
    #         .to_sql(),
    #     )

    def test_can_use_global_scopes_on_time(self):
        expected_sql = "INSERT INTO `users` (`users`.`name`, `users`.`updated_at`, `users`.`created_at`) VALUES ('Joe'"
        self.assertTrue(
            User.create({"name": "Joe"}, query=True)
            .to_sql()
            .startswith(expected_sql)
        )

    # def test_can_use_global_scopes_on_inherit(self):
    #     sql = "SELECT * FROM `user_softs` WHERE `user_softs`.`deleted_at` IS NULL"
    #     self.assertEqual(sql, UserSoft.all(query=True))
