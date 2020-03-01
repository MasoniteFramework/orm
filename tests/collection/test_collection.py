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
