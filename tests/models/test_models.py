import unittest
from src.masoniteorm.models import Model
import pendulum


class ModelTest(Model):
    __dates__ = ["due_date"]


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
