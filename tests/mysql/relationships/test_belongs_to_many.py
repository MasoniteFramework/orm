import unittest

# from src.masoniteorm import query
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import (
    has_one,
    belongs_to_many,
    has_one_through,
    has_many,
)
from dotenv import load_dotenv

load_dotenv(".env")


class User(Model):
    @has_one
    def profile(self):
        return Profile


class Profile(Model):
    pass


class Permission(Model):
    @belongs_to_many("permission_id", "role_id", "id", "id")
    def role(self):
        return Role


class PermissionSelect(Model):
    __table__ = "permissions"

    __selects__ = ["permission_id"]

    @belongs_to_many("permission_id", "role_id", "id", "id")
    def role(self):
        return Role


class Role(Model):
    @belongs_to_many("role_id", "permission_id", "id", "id")
    def permissions(self):
        return Permission


class MySQLRelationships(unittest.TestCase):
    maxDiff = None

    def test_belongs_to_many(self):
        sql = Permission.where_has(
            "role", lambda query: (query.where("slug", "users"))
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `permissions` WHERE EXISTS (SELECT * FROM `roles` INNER JOIN `permission_role` ON `roles`.`id` = `permission_role`.`role_id` WHERE `permission_role`.`permission_id` = `permissions`.`id` AND `roles`.`id` IN (SELECT `roles`.`id` FROM `roles` WHERE `roles`.`slug` = 'users'))""",
        )

    def test_belongs_to_many_has(self):
        sql = Role.has("permissions").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id`)""",
        )

    def test_belongs_to_many_or_has(self):
        sql = Role.where("name", "role_name").or_has("permissions").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE `roles`.`name` = 'role_name' OR EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id`)""",
        )

    def test_belongs_to_many_or_where_has(self):
        sql = (
            Role.where("name", "role_name")
            .or_where_has("permissions", lambda q: q.where("permission_id", 1))
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE `roles`.`name` = 'role_name' OR EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id` AND `permissions`.`id` IN (SELECT `permissions`.`id` FROM `permissions` WHERE `permissions`.`permission_id` = '1'))""",
        )

    def test_belongs_to_many_or_doesnt_have(self):
        sql = Role.where("name", "role_name").or_doesnt_have("permissions").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE `roles`.`name` = 'role_name' OR NOT EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id`)""",
        )

    def test_where_doesnt_have(self):
        sql = (
            Role.where("name", "role_name")
            .where_doesnt_have(
                "permissions", lambda q: q.where("name", "Creates Users")
            )
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE `roles`.`name` = 'role_name' AND NOT EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id` AND `permissions`.`id` IN (SELECT `permissions`.`id` FROM `permissions` WHERE `permissions`.`name` = 'Creates Users'))""",
        )

    def test_or_where_doesnt_have(self):
        sql = (
            Role.where("name", "role_name")
            .or_where_doesnt_have(
                "permissions", lambda q: q.where("name", "Creates Users")
            )
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE `roles`.`name` = 'role_name' OR NOT EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id` AND `permissions`.`id` IN (SELECT `permissions`.`id` FROM `permissions` WHERE `permissions`.`name` = 'Creates Users'))""",
        )

    def test_belongs_to_many_where_has(self):
        sql = Role.where_has(
            "permissions", lambda q: q.where("name", "Creates Users")
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `roles` WHERE EXISTS (SELECT * FROM `permissions` INNER JOIN `permission_role` ON `permissions`.`id` = `permission_role`.`permission_id` WHERE `permission_role`.`role_id` = `roles`.`id` AND `permissions`.`id` IN (SELECT `permissions`.`id` FROM `permissions` WHERE `permissions`.`name` = 'Creates Users'))""",
        )

    def test_belongs_to_many_relate_method(self):
        permission = Permission.hydrate({"id": 1, "name": "Create Users"})
        sql = permission.related("role").to_sql()

        self.assertEqual(
            sql,
            """SELECT `roles`.*, `permission_role`.`permission_id` AS permission_role_id, `permission_role`.`role_id` AS m_reserved2, `permission_role`.`id` AS m_reserved3 FROM `permissions` INNER JOIN `permission_role` ON `permission_role`.`permission_id` = `permissions`.`id` INNER JOIN `roles` ON `permission_role`.`role_id` = `roles`.`id`""",
        )

    def test_belongs_to_many_relate_method_reversed(self):
        role = Role.hydrate({"id": 1, "name": "Create Users"})
        sql = role.related("permissions").to_sql()

        self.assertEqual(
            sql,
            """SELECT `permissions`.*, `permission_role`.`role_id` AS permission_role_id, `permission_role`.`permission_id` AS m_reserved2, `permission_role`.`id` AS m_reserved3 FROM `roles` INNER JOIN `permission_role` ON `permission_role`.`role_id` = `roles`.`id` INNER JOIN `permissions` ON `permission_role`.`permission_id` = `permissions`.`id`""",
        )

    def test_belongs_to_many_joins(self):
        sql = Role.joins("permissions").to_sql()
        self.assertEqual(
            sql,
            """SELECT `roles`.*, `permission_role`.`role_id` AS permission_role_id, `permission_role`.`permission_id` AS m_reserved2, `permission_role`.`id` AS m_reserved3 FROM `roles` INNER JOIN `permission_role` ON `permission_role`.`role_id` = `roles`.`id` INNER JOIN `permissions` ON `permission_role`.`id` = `permissions`.`id`""",
        )

    def test_with_count(self):
        sql = Permission.with_count("role").to_sql()

        self.assertEqual(
            sql,
            """SELECT `permissions`.*, (SELECT COUNT(*) AS m_count_reserved FROM `permission_role` WHERE `permissions`.`id` = `permission_role`.`permission_id`) AS roles_count FROM `permissions`""",
        )

    def test_with_count_with_selects(self):
        sql = PermissionSelect.with_count("role").to_sql()

        self.assertEqual(
            sql,
            """SELECT `permissions`.`permission_id`, (SELECT COUNT(*) AS m_count_reserved FROM `permission_role` WHERE `permissions`.`id` = `permission_role`.`permission_id`) AS roles_count FROM `permissions`""",
        )
