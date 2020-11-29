import unittest
from src.masoniteorm.models import Model
import pendulum


class ModelTest(Model):
    __dates__ = ['due_date']


class TestModels(unittest.TestCase):

    def test_model_can_access_str_dates_as_pendulum(self):
        model = ModelTest.hydrate({
            'user': "joe",
            "due_date": "2020-11-28 11:42:07"
        })

        self.assertTrue(model.user)
        self.assertTrue(model.due_date)
        self.assertIsInstance(model.due_date, pendulum.now().__class__)
