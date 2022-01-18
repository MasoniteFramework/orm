import unittest

# from src.masoniteorm import query
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, has_one, belongs_to_many


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
    def test_relationship_keys(self):
        sql = User.has("profile").to_sql()
        print(sql)
        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_joins(self):
        sql = User.joins("profile").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM `users` INNER JOIN `profiles` ON `users`.`id` = `profiles`.`profile_id`""",
        )

    def test_join_on(self):
        sql = User.join_on("profile", lambda q: (q.where("active", 1))).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` INNER JOIN `profiles` ON `users`.`id` = `profiles`.`profile_id` WHERE (`profiles`.`active` = '1')""",
        )

    def test_belongs_to_many(self):
        sql = Permission.where_has(
            "role", lambda query: (query.where("slug", "users"))
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `permissions` WHERE EXISTS (SELECT `permission_role`.* FROM `permission_role` WHERE `permission_role`.`permission_id` = `permissions`.`id` AND `permission_role`.`role_id` IN (SELECT `roles`.`id` FROM `roles` WHERE `roles`.`slug` = 'users'))""",
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
