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
