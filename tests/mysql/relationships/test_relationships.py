import unittest

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
    @has_one
    def identification(self):
        return Identification


class Identification(Model):
    pass


class MySQLRelationships(unittest.TestCase):
    maxDiff = None

    def test_has(self):
        sql = User.has("profile").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_has_nested(self):
        sql = User.has("profile.identification").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `profiles`.`id`))""",
        )

    def test_or_has(self):
        sql = User.where("name", "Joe").or_has("profile").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' OR EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_or_has_nested(self):
        sql = User.where("name", "Joe").or_has("profile.identification").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' OR EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `profiles`.`id`))""",
        )

    def test_relationship_where_has(self):
        sql = (
            User.where("name", "Joe")
            .where_has("profile", lambda q: q.where("profile_id", 1))
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' AND EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_where_has_nested(self):
        sql = (
            User.where("name", "Joe")
            .where_has(
                "profile.identification", lambda q: q.where("identification_id", 1)
            )
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' AND EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `profiles`.`id` AND `identifications`.`identification_id` = '1'))""",
        )

    def test_relationship_or_where_has(self):
        sql = (
            User.where("name", "Joe")
            .or_where_has("profile", lambda q: q.where("profile_id", 1))
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' OR EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_or_where_has_nested(self):
        sql = (
            User.where("name", "Joe")
            .or_where_has(
                "profile.identification", lambda q: q.where("identification_id", 1)
            )
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE `users`.`name` = 'Joe' OR EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `profiles`.`id` AND `identifications`.`identification_id` = '1'))""",
        )

    def test_relationship_doesnt_have(self):
        sql = User.doesnt_have("profile").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`)""",
        )

    def test_relationship_doesnt_have_nested(self):
        sql = User.doesnt_have("profile.identification").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `profiles`.`id`))""",
        )

    def test_relationship_where_doesnt_have(self):
        sql = User.where_doesnt_have(
            "profile", lambda q: q.where("profile_id", 1)
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_where_doesnt_have_nested(self):
        sql = User.where_doesnt_have(
            "profile.identification", lambda q: q.where("identification_id", 1)
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`) AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `users`.`id` AND `identifications`.`identification_id` = '1')""",
        )

    def test_relationship_or_where_doesnt_have(self):
        sql = User.or_where_doesnt_have(
            "profile", lambda q: q.where("profile_id", 1)
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id` AND `profiles`.`profile_id` = '1')""",
        )

    def test_relationship_or_where_doesnt_have_nested(self):
        sql = User.or_where_doesnt_have(
            "profile.identification", lambda q: q.where("identification_id", 1)
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `users` WHERE NOT EXISTS (SELECT * FROM `profiles` WHERE `profiles`.`profile_id` = `users`.`id`) AND EXISTS (SELECT * FROM `identifications` WHERE `identifications`.`identification_id` = `users`.`id` AND `identifications`.`identification_id` = '1')""",
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
