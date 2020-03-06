import unittest

from src.masonite.orm.collection.Collection import Collection


class TestCollection(unittest.TestCase):
    def test_take(self):
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.take(2), [1, 2])

    def test_first(self):
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.first(), 1)
        self.assertEqual(collection.last(), 4)
        self.assertEqual(collection.first(lambda x: x < 3), 1)

    def test_last(self):
        collection = Collection([1, 2, 3, 4])
        self.assertEqual(collection.last(), 4)
        self.assertEqual(collection.last(lambda x: x < 3), 2)

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

        self.assertEqual(collection.get(0), [1, 1])

        self.assertIsNone(collection.get(2))
        self.assertEqual(collection.get(2, 0), 0)

    def test_merge(self):
        collection = Collection([[1, 1], [2, 4]])
        collection.merge([[2, 1]])
        self.assertEqual(collection.all(), [[1, 1], [2, 4], [2, 1]])

    def test_reduce(self):
        callback = lambda x, y: x + y
        collection = Collection([1, 1, 2, 4])
        sum = collection.sum()

        reduce = collection.reduce(callback)
        self.assertEqual(sum, reduce)

        reduce = collection.reduce(callback, 10)

        self.assertEqual(10 + sum, reduce)

    def test_forget(self):
        collection = Collection([1, 2, 3, 4])
        collection.forget(0)
        self.assertEqual(collection.all(), [2, 3, 4])

        collection.forget(1, 2)
        self.assertEqual(collection.all(), [2])
        collection.forget(0)
        self.assertTrue(collection.is_empty())

    def test_prepend(self):
        collection = Collection([1, 2, 3, 4])
        collection.prepend(0)

        self.assertEqual(collection.get(0), 0)
        self.assertEqual(collection.all(), [0, 1, 2, 3, 4])

    def test_pull(self):
        collection = Collection([1, 2, 3, 4])
        value = collection.pull(0)

        self.assertEqual(value, 1)
        self.assertEqual(collection.all(), [2, 3, 4])

    def test_push(self):
        collection = Collection([1, 2, 3, 4])
        collection.push(5)

        self.assertEqual(collection.get(4), 5)
        self.assertEqual(collection.all(), [1, 2, 3, 4, 5])

    def test_put(self):
        collection = Collection([1, 2, 3, 4])
        collection.put(2, 5)

        self.assertEqual(collection.get(2), 5)
        self.assertEqual(collection.all(), [1, 2, 5, 4])

    def test_reject(self):
        collection = Collection([1, 2, 3, 4])
        collection.reject(lambda x: x if x > 2 else None)

        self.assertEqual(collection.all(), [3, 4])

        collection = Collection(
            [
                {"name": "Corentin All", "age": 1},
                {"name": "Corentin All", "age": 2},
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]
        )
        collection.reject(lambda x: x if x['age'] > 2 else None)

        self.assertEqual(Collection(
            [
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]), collection.all())

        collection.reject(lambda x: x['age'] if x['age'] > 2 else None)

        self.assertEqual(collection.all(), [3, 4])

    def test_for_page(self):
        collection = Collection([1, 2, 3, 4])
        chunked = collection.for_page(0, 3)

        self.assertEqual(chunked.all(), [1, 2, 3])

    def test_unique(self):
        collection = Collection([1, 1, 2, 3, 4])
        unique = collection.unique()

        self.assertEqual(unique.all(), [1, 2, 3, 4])

        collection = Collection(
            [
                {"name": "Corentin All", "age": 1},
                {"name": "Corentin All", "age": 1},
                {"name": "Corentin All", "age": 2},
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]
        )

        unique = collection.unique('age')

        self.assertEqual(unique.all(), [
            {"name": "Corentin All", "age": 1},
            {"name": "Corentin All", "age": 2},
            {"name": "Corentin All", "age": 3},
            {"name": "Corentin All", "age": 4},
        ])

    def test_transform(self):
        collection = Collection([1, 1, 2, 3, 4])
        collection.transform(lambda x: x * 2)

        self.assertEqual(collection.all(), [2, 2, 4, 6, 8])

    def test_shift(self):
        collection = Collection([1, 2, 3, 4])
        value = collection.shift()

        self.assertEqual(value, 1)
        self.assertEqual(collection.all(), [2, 3, 4])

        collection = Collection(
            [
                {"name": "Corentin All", "age": 1},
                {"name": "Corentin All", "age": 2},
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]
        )

        value = collection.shift()
        self.assertEqual(value, {"name": "Corentin All", "age": 1})
        self.assertEqual(collection.all(), [
            {"name": "Corentin All", "age": 2},
            {"name": "Corentin All", "age": 3},
            {"name": "Corentin All", "age": 4},
        ])

    def test_sort(self):
        collection = Collection([4, 1, 2, 3])
        collection.sort()

        self.assertEqual(collection.all(), [1, 2, 3, 4])

    def test_reverse(self):
        collection = Collection([4, 1, 2, 3])
        collection.reverse()

        self.assertEqual(collection.all(), [3, 2, 1, 4])

        collection = Collection(
            [
                {"name": "Corentin All", "age": 2},
                {"name": "Corentin All", "age": 3},
                {"name": "Corentin All", "age": 4},
            ]
        )
        collection.reverse()

        self.assertEqual(collection.all(), [
            {"name": "Corentin All", "age": 4},
            {"name": "Corentin All", "age": 3},
            {"name": "Corentin All", "age": 2},
        ])

    def test_zip(self):
        collection = Collection(['Chair', 'Desk'])
        zipped = collection.zip([100, 200])

        self.assertEqual(zipped.all(), [['Chair', 100], ['Desk', 200]])

    def test_diff(self):
        collection = Collection(['Chair', 'Desk'])
        diff = collection.diff([100, 200])

        self.assertEqual(diff.all(), ['Chair', 'Desk'])

    def test_each(self):
        collection = Collection([1, 2, 3, 4])
        collection.each(lambda x: x + 2)
        self.assertEqual(collection.all(), [x + 2 for x in range(1, 5)])

    def test_every(self):
        collection = Collection([1, 2, 3, 4])
        self.assertFalse(collection.every(lambda x: x > 2))

        collection = Collection([1, 2, 3, 4])
        self.assertTrue(collection.every(lambda x: x >= 1))

    def test_filter(self):
        collection = Collection([1, 2, 3, 4])
        filtered = collection.filter(lambda x: x > 2)
        self.assertEqual(filtered.all(), Collection([3, 4]))

    def test_implode(self):
        collection = Collection([1, 2, 3, 4])
        result = collection.implode('-')
        self.assertEqual(result, '1-2-3-4')

        collection = Collection([{"name": "Corentin"}, {"name": "Joe"}, {"name": "Marlysson"}, ])
        result = collection.implode(key='name')
        self.assertEqual(result, "Corentin,Joe,Marlysson")

    def test_map_into(self):
        collection = Collection(['USD', 'EUR', 'GBP'])

        class Currency:
            def __init__(self, code):
                self.code = code

            def __eq__(self, other):
                return self.code == other.code

        currencies = collection.map_into(Currency)
        self.assertEqual(
            currencies.all(), [Currency('USD'), Currency('EUR'), Currency('GBP')]
        )

    def test_map(self):
        collection = Collection([1, 2, 3, 4])
        multiplied = collection.map(lambda x: x * 2)
        self.assertEqual(multiplied.all(), [2, 4, 6, 8])

        def callback(x):
            x["age"] = x["age"] + 2
            return x

        collection = Collection([
            {"name": "Corentin", "age": 10}, {"name": "Joe", "age": 20}, {"name": "Marlysson", "age": 15}
        ])
        result = collection.map(callback)
        self.assertEqual(result.all(), [
            {"name": "Corentin", "age": 12}, {"name": "Joe", "age": 22}, {"name": "Marlysson", "age": 17}

        ])
