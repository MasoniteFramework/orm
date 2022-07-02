import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import has_one, belongs_to_many, has_one_through, has_many
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


class InboundShipment(Model):
    @has_one_through("port_id", "country_id", "from_port_id", "country_id")
    def from_country(self):
        return Country, Port


class Country(Model):
    pass


class Port(Model):
    pass


class MySQLRelationships(unittest.TestCase):
    maxDiff = None

    def test_has(self):
        sql = User.has("profile").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_or_has(self):
        sql = User.where("name", "Joe").or_has("profile").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' OR EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_relationship_where_has(self):
        sql = User.where("name", "Joe").where_has("profile", lambda q: q.where("profile_id", 1)).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' AND EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_or_where_has(self):
        sql = User.where("name", "Joe").or_where_has("profile", lambda q: q.where("profile_id", 1)).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' OR EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_doesnt_have(self):
        sql = User.doesnt_have("profile").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_relationship_where_doesnt_have(self):
        sql = User.where_doesnt_have("profile", lambda q: q.where("profile_id", 1)).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_or_where_doesnt_have(self):
        sql = User.or_where_doesnt_have("profile", lambda q: q.where("profile_id", 1)).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
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
