import datetime
import json
import os
import unittest

import pendulum

from src.masoniteorm.collection import Collection
from src.masoniteorm.models import Model
from tests.User import User

if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class ProfileFillable(Model):
        __fillable__ = ["name"]
        __table__ = "profiles"
        __timestamps__ = None

    class ProfileFillTimeStamped(Model):
        __fillable__ = ["*"]
        __table__ = "profiles"

    class ProfileFillAsterisk(Model):
        __fillable__ = ["*"]
        __table__ = "profiles"
        __timestamps__ = None

    class ProfileGuarded(Model):
        __guarded__ = ["email"]
        __table__ = "profiles"
        __timestamps__ = None

    class ProfileSerialize(Model):
        __fillable__ = ["*"]
        __table__ = "profiles"
        __hidden__ = ["password"]

    class ProfileSerializeWithVisible(Model):
        __fillable__ = ["*"]
        __table__ = "profiles"
        __visible__ = ["name", "email"]

    class ProfileSerializeWithVisibleAndHidden(Model):
        __fillable__ = ["*"]
        __table__ = "profiles"
        __visible__ = ["name", "email"]
        __hidden__ = ["password"]

    class Profile(Model):
        pass

    class Company(Model):
        pass

    class User(Model):
        @property
        def meta(self):
            return {"is_subscribed": True}

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

        def test_can_use_guarded(self):
            sql = ProfileGuarded.create(
                {"name": "Joe", "email": "user@example.com"}, query=True
            )

            self.assertEqual(
                sql, "INSERT INTO `profiles` (`profiles`.`name`) VALUES ('Joe')"
            )

        def test_can_use_guarded_asterisk(self):
            sql = ProfileFillAsterisk.create(
                {"name": "Joe", "email": "user@example.com"}, query=True
            )

            self.assertEqual(
                sql,
                "INSERT INTO `profiles` (`profiles`.`name`, `profiles`.`email`) VALUES ('Joe', 'user@example.com')",
            )

        def test_can_touch(self):
            profile = ProfileFillTimeStamped.hydrate({"name": "Joe", "id": 1})

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
            # self.assertIsInstance(User.first(), User)
            # self.assertIsInstance(User.first(), User)

        def test_serialize(self):
            profile = ProfileFillAsterisk.hydrate({"name": "Joe", "id": 1})

            self.assertEqual(profile.serialize(), {"name": "Joe", "id": 1})

        def test_json(self):
            profile = ProfileFillAsterisk.hydrate({"name": "Joe", "id": 1})

            self.assertEqual(profile.to_json(), '{"name": "Joe", "id": 1}')

        def test_serialize_with_hidden(self):
            profile = ProfileSerialize.hydrate(
                {"name": "Joe", "id": 1, "password": "secret"}
            )

            self.assertTrue(profile.serialize().get("name"))
            self.assertTrue(profile.serialize().get("id"))
            self.assertFalse(profile.serialize().get("password"))

        def test_serialize_with_visible(self):
            profile = ProfileSerializeWithVisible.hydrate(
                {
                    "name": "Joe",
                    "id": 1,
                    "password": "secret",
                    "email": "joe@masonite.com",
                }
            )
            self.assertTrue(
                {"name": "Joe", "email": "joe@masonite.com"}, profile.serialize()
            )

        def test_serialize_with_visible_and_hidden_raise_error(self):
            profile = ProfileSerializeWithVisibleAndHidden.hydrate(
                {
                    "name": "Joe",
                    "id": 1,
                    "password": "secret",
                    "email": "joe@masonite.com",
                }
            )
            with self.assertRaises(AttributeError):
                profile.serialize()

        def test_serialize_with_on_the_fly_appends(self):
            user = User.hydrate({"name": "Joe", "id": 1})

            user.set_appends(["meta"])

            serialized = user.serialize()
            self.assertEqual(serialized["id"], 1)
            self.assertEqual(serialized["name"], "Joe")
            self.assertEqual(serialized["meta"]["is_subscribed"], True)

        def test_serialize_with_model_appends(self):
            User.__appends__ = ["meta"]
            user = User.hydrate({"name": "Joe", "id": 1})
            serialized = user.serialize()
            self.assertEqual(serialized["id"], 1)
            self.assertEqual(serialized["name"], "Joe")
            self.assertEqual(serialized["meta"]["is_subscribed"], True)

        def test_serialize_with_date(self):
            user = User.hydrate({"name": "Joe", "created_at": pendulum.now()})

            self.assertTrue(json.dumps(user.serialize()))

        def test_set_as_date(self):
            user = User.hydrate(
                {
                    "name": "Joe",
                    "created_at": pendulum.now().add(days=10).to_datetime_string(),
                }
            )

            self.assertTrue(user.created_at)
            self.assertTrue(user.created_at.is_future())

        def test_access_as_date(self):
            user = User.hydrate(
                {
                    "name": "Joe",
                    "created_at": datetime.datetime.now() + datetime.timedelta(days=1),
                }
            )

            self.assertTrue(user.created_at)
            self.assertTrue(user.created_at.is_future())

        def test_hydrate_with_none(self):
            profile = ProfileFillAsterisk.hydrate(None)

            self.assertEqual(profile, None)

        def test_can_find_first(self):
            profile = User.find(1)

        def test_serialize_with_dirty_attribute(self):
            profile = ProfileFillAsterisk.hydrate({"name": "Joe", "id": 1})

            profile.age = 18
            self.assertEqual(profile.serialize(), {"age": 18, "name": "Joe", "id": 1})

        def test_attribute_check_with_hasattr(self):
            self.assertFalse(hasattr(Profile(), "__password__"))
