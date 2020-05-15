import unittest
from src.masonite.orm.grammar.mssql_grammar import MSSQLGrammar
from app.User import User
from src.masonite.orm.collection import Collection
from src.masonite.orm.models import Model
import os

if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class ProfileFillable(Model):
        __fillable__ = ["name"]
        __table__ = "profiles"

    class ProfileFillAsterisk(Model):
        __fillable__ = ["*"]
        __table__ = "profiles"

    class Profile(Model):
        pass

    class Company(Model):
        pass

    class User(Model):
        pass

    class ProductNames(Model):
        pass

    class TestModel(unittest.TestCase):
        def test_can_use_fillable(self):
            sql = ProfileFillable.create(
                {"name": "Joe", "email": "user@example.com"}, query=True
            )

            self.assertEqual(
                sql, "INSERT INTO `profiles` (`profiles`.`name`) VALUES ('Joe')"
            )

        def test_can_use_fillable_asterisk(self):
            sql = ProfileFillAsterisk.create(
                {"name": "Joe", "email": "user@example.com"}, query=True
            )

            self.assertEqual(
                sql,
                "INSERT INTO `profiles` (`profiles`.`name`, `profiles`.`email`) VALUES ('Joe', 'user@example.com')",
            )

        def test_can_touch(self):
            profile = ProfileFillAsterisk.hydrate({"name": "Joe", "id": 1})

            sql = profile.touch("now", query=True)

            self.assertEqual(
                sql,
                "UPDATE `profiles` SET `profiles`.`updated_at` = 'now' WHERE `profiles`.`id` = '1'",
            )

        def test_table_name(self):
            table_name = Profile.get_table_name()
            self.assertEqual(table_name, "profiles")

            table_name = Company.get_table_name()
            self.assertEqual(table_name, "companies")

            table_name = ProductNames.get_table_name()
            self.assertEqual(table_name, "product_names")

        def test_returns_correct_data_type(self):
            self.assertIsInstance(User.all(), Collection)
            self.assertIsInstance(User.first(), User)

        def test_serialize(self):
            profile = ProfileFillAsterisk.hydrate({"name": "Joe", "id": 1})

            self.assertEqual(profile.serialize(), {"name": "Joe", "id": 1})

        def test_hydrate_with_none(self):
            profile = ProfileFillAsterisk.hydrate(None)

            self.assertEqual(profile, None)

        def test_can_find_first(self):
            profile = User.find(1)
            print(profile)

        def test_can_print_none(self):
            print(User.where("remember_token", "10").first())

        def test_serialize_with_dirty_attribute(self):
            profile = ProfileFillAsterisk.hydrate({"name": "Joe", "id": 1})

            profile.age = 18
            self.assertEqual(profile.serialize(), {"age": 18, "name": "Joe", "id": 1,})

        def test_attribute_check_with_hasattr(self):
            self.assertFalse(hasattr(Profile(), "__password__"))
