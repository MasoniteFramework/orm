import datetime
import json
import unittest

import pendulum

from src.masoniteorm.models import Model


class ModelTest(Model):
    __dates__ = ["due_date"]
    __casts__ = {
        "is_vip": "bool",
        "payload": "json",
        "x": "int",
        "f": "float",
        "d": "decimal",
    }


class FillableModelTest(Model):
    __fillable__ = ["due_date", "is_vip"]


class InvalidFillableGuardedModelTest(Model):
    __fillable__ = ["due_date"]
    __guarded__ = ["is_vip", "payload"]


class InvalidFillableGuardedChildModelTest(ModelTest):
    __fillable__ = ["due_date"]
    __guarded__ = ["is_vip", "payload"]


class ModelTestForced(Model):
    __table__ = "users"
    __force_update__ = True


class TestModels(unittest.TestCase):
    def test_model_can_access_str_dates_as_pendulum(self):
        model = ModelTest.hydrate({"user": "joe", "due_date": "2020-11-28 11:42:07"})

        self.assertTrue(model.user)
        self.assertTrue(model.due_date)
        self.assertIsInstance(model.due_date, pendulum.now().__class__)

    def test_model_can_access_str_dates_as_pendulum_from_correct_datetimes(self):
        model = ModelTest()

        self.assertEqual(
            model.get_new_date(datetime.datetime(2021, 1, 1, 7, 10)).hour, 7
        )
        self.assertEqual(model.get_new_date(datetime.date(2021, 1, 1)).hour, 0)
        self.assertEqual(model.get_new_date(datetime.time(1, 1, 1)).hour, 1)
        self.assertEqual(model.get_new_date("2020-11-28 11:42:07").hour, 11)

    def test_model_can_access_str_dates_on_relationships(self):
        model = ModelTest.hydrate({"user": "joe", "due_date": "2020-11-28 11:42:07"})
        model.add_relation(
            {
                "profile": ModelTest.hydrate(
                    {"name": "bob", "due_date": "2020-11-28 11:42:07"}
                )
            }
        )

        self.assertEqual(model.profile.name, "bob")
        self.assertTrue(model.profile.due_date.is_past())

    def test_model_original_and_dirty_attributes(self):
        model = ModelTest.hydrate({"username": "joe", "admin": True})

        self.assertEqual(model.username, "joe")
        self.assertEqual(
            model.__original_attributes__, {"username": "joe", "admin": True}
        )

        model.username = "bob"

        self.assertEqual(model.username, "bob")
        self.assertEqual(model.get_original("username"), "joe")
        self.assertEqual(model.get_dirty("username"), "bob")
        self.assertEqual(model.__dirty_attributes__["username"], "bob")
        self.assertEqual(model.get_dirty_keys(), ["username"])
        self.assertTrue(model.is_dirty() is True)
        self.assertEqual(
            model.__original_attributes__, {"username": "joe", "admin": True}
        )

    def test_model_creates_when_new(self):
        model = ModelTest.hydrate({"id": 1, "username": "joe", "admin": True})

        model.name = "Bill"
        sql = model.save(query=True)
        self.assertTrue(sql.startswith("UPDATE"))

        model = ModelTest()

        model.name = "Bill"
        sql = model.save(query=True)
        self.assertTrue(sql.startswith("INSERT"))

    def test_model_can_cast_attributes(self):
        model = ModelTest.hydrate(
            {
                "is_vip": 1,
                "payload": '["item1", "item2"]',
                "x": True,
                "f": "10.5",
                "d": 3.14,
            }
        )

        self.assertEqual(type(model.payload), list)
        self.assertEqual(type(model.x), int)
        self.assertEqual(type(model.f), float)
        self.assertEqual(type(model.is_vip), bool)
        self.assertEqual(type(model.serialize()["is_vip"]), bool)

    def test_model_can_cast_dict_attributes(self):
        """test cast with dict object to json field"""
        dictcasttest = {}
        dictcasttest["key"] = "value"
        model = ModelTest.hydrate(
            {"is_vip": 1, "payload": dictcasttest, "x": True, "f": "10.5"}
        )

        self.assertEqual(type(model.payload), dict)
        self.assertEqual(type(model.x), int)
        self.assertEqual(type(model.f), float)
        self.assertEqual(type(model.is_vip), bool)
        self.assertEqual(type(model.serialize()["is_vip"]), bool)

    def test_valid_json_cast(self):
        model = ModelTest.hydrate(
            {"payload": {"this": "dict", "is": "usable", "as": "json"}}
        )

        self.assertEqual(type(model.payload), dict)

        model = ModelTest.hydrate(
            {"payload": {"this": "dict", "is": "invalid", "as": "json"}}
        )

        self.assertEqual(type(model.payload), dict)

        model = ModelTest.hydrate(
            {"payload": '{"this": "dict", "is": "usable", "as": "json"}'}
        )

        self.assertEqual(type(model.payload), dict)

        model = ModelTest.hydrate({"payload": '{"valid": "json", "int": 1}'})

        self.assertEqual(type(model.payload), dict)

        model = ModelTest.hydrate({"payload": "{'this': 'should', 'throw': 'error'}"})

        self.assertEqual(model.payload, None)

        with self.assertRaises(ValueError):
            model.payload = "{'this': 'should', 'throw': 'error'}"
            model.save()

    def test_model_update_without_changes(self):
        model = ModelTest.hydrate(
            {"id": 1, "username": "joe", "name": "Joe", "admin": True}
        )

        model.username = "joe"
        model.name = "Bill"
        sql = model.save(query=True)
        self.assertTrue(sql.startswith("UPDATE"))
        self.assertNotIn("username", sql)

    def test_force_update_on_model_class(self):
        model = ModelTestForced.hydrate(
            {"id": 1, "username": "joe", "name": "Joe", "admin": True}
        )

        model.username = "joe"
        model.name = "Bill"
        sql = model.save(query=True)
        self.assertTrue(sql.startswith("UPDATE"))
        self.assertIn("username", sql)
        self.assertIn("name", sql)

    def test_only_method(self):
        model = ModelTestForced.hydrate(
            {"id": 1, "username": "joe", "name": "Joe", "admin": True}
        )

        self.assertEqual({"username": "joe"}, model.only("username"))
        self.assertEqual({"username": "joe"}, model.only(["username"]))

    def test_model_update_without_changes_at_all(self):
        model = ModelTest.hydrate(
            {"id": 1, "username": "joe", "name": "Joe", "admin": True}
        )

        model.username = "joe"
        model.name = "Joe"
        sql = model.save(query=True)
        self.assertFalse(sql.startswith("UPDATE"))

    def test_model_using_or_where(self):
        model = ModelTest()
        sql = model.where("name", "=", "joe").or_where("is_vip", True).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `model_tests` WHERE `model_tests`.`name` = 'joe' OR `model_tests`.`is_vip` = '1'""",
        )

    def test_model_using_or_where_and_chaining_wheres(self):
        model = ModelTest()

        sql = (
            model.where("name", "=", "joe")
            .or_where(
                lambda query: query.where("username", "Joseph").or_where(
                    "age", ">=", 18
                )
            )
            .to_sql()
        )

        self.assertTrue(
            sql,
            """SELECT * FROM `model_tests` WHERE `model_tests`.`name` = 'joe' OR (`model_tests`.`username` = 'Joseph' OR `model_tests`.`age` >= '18'))""",
        )

    def test_both_fillable_and_guarded_attributes_raise(self):
        # Both fillable and guarded props are populated on this class
        with self.assertRaises(AttributeError):
            InvalidFillableGuardedModelTest()
        # Child that inherits from an intermediary class also fails
        with self.assertRaises(AttributeError):
            InvalidFillableGuardedChildModelTest()
        # Still shouldn't be allowed to define even if empty
        InvalidFillableGuardedModelTest.__fillable__ = []
        with self.assertRaises(AttributeError):
            InvalidFillableGuardedModelTest()
        # Or wildcard
        InvalidFillableGuardedModelTest.__fillable__ = ["*"]
        with self.assertRaises(AttributeError):
            InvalidFillableGuardedModelTest()
        # Empty guarded attr still raises
        InvalidFillableGuardedModelTest.__guarded__ = []
        with self.assertRaises(AttributeError):
            InvalidFillableGuardedModelTest()
        # Removing one of the props allows us to instantiate
        delattr(InvalidFillableGuardedModelTest, "__guarded__")
        InvalidFillableGuardedModelTest()
