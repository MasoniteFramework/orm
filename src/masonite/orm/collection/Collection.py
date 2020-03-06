class Collection:
    def __init__(self, items=[]):
        self._items = items

    def take(self, number):
        return self._items[:number]

    def first(self):
        return self._items[0]

    def last(self):
        return self._items[-1]

    def all(self):
        return self._items

    def __len__(self):
        return len(self._items)

    def avg(self, key=None):
        result = 0
        items = self._get_value(key) or self._items
        try:
            result = sum(items) / len(items)
        except TypeError:
            pass
        return result

    def chunk(self, step):
        items = []
        for i in range(0, self.count(), step):
            items.append(self.__class__(self._items[i:i + step]))
        return self.__class__(items)

    def collapse(self):
        items = []
        for item in self._items:
            if isinstance(item, Collection):
                item = item.all()
            items += item
        return self.__class__(items)

    def contains(self):
        pass

    def count(self):
        return len(self._items)

    def diff(self):
        pass

    def each(self):
        pass

    def every(self):
        pass

    def filter(self):
        pass

    def flatten(self):
        pass

    def forget(self):
        pass

    def for_page(self):
        pass

    def get(self):
        return self.all()

    def implode(self):
        pass

    def is_empty(self):
        return not self._items

    def map(self):
        pass

    def map_into(self, cls, method=None):
        results = []
        for item in self._items:

            if method:
                results.append(getattr(cls, method)(item))
            else:
                results.append(cls(item))

        return Collection(results)

    def merge(self, items):
        if not isinstance(items, list):
            raise ValueError('Unable to merge uncompatible types')

        if isinstance(items, Collection):
            items = items.all()

        self._items += items
        return self

    def pluck(self, attribute):
        attributes = []
        for item in self._items:
            for key, value in item.items():
                if key == attribute:
                    attributes.append(value)
        return attributes

    def pop(self):
        last = self._items.pop()
        return last

    def prepend(self):
        pass

    def pull(self):
        pass

    def push(self):
        pass

    def put(self):
        pass

    def reduce(self):
        pass

    def reject(self):
        pass

    def reverse(self):
        pass

    def serialize(self):
        pass

    def shift(self):
        pass

    def sort(self):
        pass

    def sum(self, key=None):
        result = 0
        items = self._get_value(key) or self._items
        try:
            result = sum(items)
        except TypeError:
            pass
        return result

    def to_json(self):
        pass

    def transform(self):
        pass

    def unique(self):
        pass

    def where(self, attribute, value):
        attributes = []
        for item in self._items:
            if item.get(attribute) == value:
                attributes.append(item)

        return attributes or None

    def zip(self):
        pass

    def __iter__(self):
        for item in self._items:
            yield item

    def __eq__(self, other):
        return self.all() == other.all()

    def _get_value(self, key):
        if not key:
            return None

        items = []
        for item in self._items:
            if isinstance(key, str):
                if hasattr(item, key) or (key in item):
                    items.append(getattr(item, key, item[key]))
            elif callable(key):
                items.append(key(item))
        return items
