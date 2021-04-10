import unittest
from src.masoniteorm.models import Model
import pendulum


class ModelTest(Model):
    __dates__ = ["due_date"]
    __casts__ = {"is_vip": "bool", "payload": "json", "x": "int", "f": "float"}


class TestModels(unittest.TestCase):
    def test_model_can_access_str_dates_as_pendulum(self):
        model = ModelTest.hydrate({"user": "joe", "due_date": "2020-11-28 11:42:07"})

        self.assertTrue(model.user)
        self.assertTrue(model.due_date)
        self.assertIsInstance(model.due_date, pendulum.now().__class__)

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
            {"is_vip": 1, "payload": '{"key": "value"}', "x": True, "f": "10.5"}
        )

        self.assertEqual(type(model.payload), dict)
        self.assertEqual(type(model.x), int)
        self.assertEqual(type(model.f), float)
        self.assertEqual(type(model.is_vip), bool)
        self.assertEqual(type(model.serialize()["is_vip"]), bool)

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
        ModelTest.__force_update__ = True
        model = ModelTest.hydrate(
            {"id": 1, "username": "joe", "name": "Joe", "admin": True}
        )

        model.username = "joe"
        model.name = "Bill"
        sql = model.save(query=True)
        self.assertTrue(sql.startswith("UPDATE"))
        self.assertIn("username", sql)
        self.assertIn("name", sql)

    def test_model_update_without_changes_at_all(self):
        model = ModelTest.hydrate(
            {"id": 1, "username": "joe", "name": "Joe", "admin": True}
        )

        model.username = "joe"
        model.name = "Joe"
        sql = model.save(query=True)
        # it's working but update timestamps, the update should be discarded/abandonned ?
