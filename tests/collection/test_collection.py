import unittest

from src.masonite.orm.collection.Collection import Collection


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

    def test_sum(self):
        collection = Collection([1, 1, 2, 4])
        self.assertEqual(collection.sum(), 8)

        collection = Collection(
            [
                {"name": "Corentin All", "age": 1},
                {"name": "Corentin All", "age": 2},
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]
        )
        self.assertEqual(collection.sum("age"), 10)
        self.assertEqual(collection.sum(), 0)

        collection = Collection(
            [
                {"name": "chair", "colours": ["green", "black"]},
                {"name": "desk", "colours": ["red", "yellow"]},
                {"name": "bookcase", "colours": ["white"]},
            ]
        )
        self.assertEqual(collection.sum(lambda x: len(x["colours"])), 5)
        self.assertEqual(collection.sum(lambda x: len(x)), 6)

    def test_avg(self):
        collection = Collection([1, 1, 2, 4])
        self.assertEqual(collection.avg(), 2)

        collection = Collection(
            [
                {"name": "Corentin All", "age": 1},
                {"name": "Corentin All", "age": 2},
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]
        )
        self.assertEqual(collection.avg("age"), 2.5)
        self.assertEqual(collection.avg(), 0)

        collection = Collection(
            [
                {"name": "chair", "colours": ["green", "black"]},
                {"name": "desk", "colours": ["red", "yellow"]},
                {"name": "bookcase", "colours": ["white"]},
            ]
        )
        self.assertEqual(collection.avg(lambda x: len(x["colours"])), 5 / 3)
        self.assertEqual(collection.avg(lambda x: len(x)), 2)

    def test_count(self):
        collection = Collection([1, 1, 2, 4])
        self.assertEqual(collection.count(), 4)

        collection = Collection(
            [{"name": "Corentin All", "age": 1}, {"name": "Corentin All", "age": 2}, ]
        )
        self.assertEqual(collection.count(), 2)

    def test_chunk(self):
        collection = Collection([1, 1, 2, 4])

        chunked = collection.chunk(2)
        self.assertEqual(
            chunked, Collection([
                Collection([1, 1]), Collection([2, 4])
            ])
        )

        collection = Collection(
            [
                {"name": "chair", "colours": ["green", "black"]},
                {"name": "desk", "colours": ["red", "yellow"]},
                {"name": "bookcase", "colours": ["white"]},
            ]
        )

        chunked = collection.chunk(2)
        self.assertEqual(
            chunked, Collection([
                Collection([
                    {"name": "chair", "colours": ["green", "black"]},
                    {"name": "desk", "colours": ["red", "yellow"]}]),
                Collection([
                    {"name": "bookcase", "colours": ["white"]},
                ])
            ])
        )

    def test_collapse(self):
        collection = Collection([[1, 1], [2, 4]])

        collapsed = collection.collapse()

        self.assertEqual(collapsed, Collection([1, 1, 2, 4]))

    def test_get(self):
        collection = Collection([[1, 1], [2, 4]])

        self.assertEqual(collection.get(), [[1, 1], [2, 4]])

    def test_merge(self):
        collection = Collection([[1, 1], [2, 4]])
        collection.merge([[2, 1]])
        self.assertEqual(collection.all(), [[1, 1], [2, 4], [2, 1]])
