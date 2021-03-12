import unittest
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, has_one


class User(Model):
    @has_one
    def profile(self):
        return Profile


class Profile(Model):
    pass


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
