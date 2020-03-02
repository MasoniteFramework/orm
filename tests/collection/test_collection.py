from src.masonite.orm.collection.Collection import Collection
import unittest


class TestCollection(unittest.TestCase):
    def test_take(self):
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.take(2), [1, 2])

    def test_first(self):
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.first(), 1)

    def test_last(self):
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.last(), 4)

    def test_pluck(self):
        collection = Collection([{"id": 1, "name": "Joe"}, {"id": 2, "name": "Bob"}])
        self.assertEqual(collection.pluck("id"), [1, 2])

    def test_where(self):
        collection = Collection(
            [
                {"id": 1, "name": "Joe"},
                {"id": 2, "name": "Joe"},
                {"id": 3, "name": "Bob"},
            ]
        )
        self.assertEqual(len(collection.where("name", "Joe")), 2)

    def test_pop(self):
        collection = Collection([1, 2, 3])
        self.assertEqual(collection.pop(), 3)
        self.assertEqual(collection.all(), [1, 2])

    def test_is_empty(self):
        collection = Collection([])
        self.assertEqual(collection.is_empty(), True)
        collection = Collection([1, 2, 3])
        self.assertEqual(collection.is_empty(), False)
