from functools import reduce


class Collection:
    def __init__(self, items=[]):
        self._items = items

    def take(self, number):
        if number < 0:
            return self[number:]

        return self[:number]

    def first(self, callback=None):
        filtered = self
        if callback:
            filtered = self.filter(callback)
        return filtered[0]

    def last(self, callback=None):
        filtered = self
        if callback:
            filtered = self.filter(callback)
        return filtered[-1]

    def all(self):
        return self._items

    def avg(self, key=None):
        result = 0
        items = self._get_value(key) or self._items
        try:
            result = sum(items) / len(items)
        except TypeError:
            pass
        return result

    def chunk(self, size):
        items = []
        for i in range(0, self.count(), size):
            items.append(self[i:i + size])
        return self.__class__(items)

    def collapse(self):
        items = []
        for item in self:
            if isinstance(item, Collection):
                item = item.all()
            items += item
        return self.__class__(items)

    def contains(self):
        # todo implements this methods
        pass

    def count(self):
        return len(self._items)

    def diff(self, items):
        if isinstance(items, Collection):
            items = items.all()
        return self.__class__([x for x in self if x not in items])

    def each(self, callback):
        self._check_is_callable(callback)

        for k, v in enumerate(self):
            result = callback(v)
            if not result:
                break
            self[k] = result

    def every(self, callback):
        self._check_is_callable(callback)
        return all([callback(x) for x in self])

    def filter(self, callback):
        self._check_is_callable(callback)
        return self.__class__(list(filter(callback, self)))

    def flatten(self):
        # todo implements this methods
        pass

    def forget(self, *keys):
        keys = reversed(sorted(keys))

        for key in keys:
            del self[key]

        return self

    def for_page(self, page, number):
        return self.__class__(self[page:number])

    def get(self, key, default=None):
        try:
            return self[key]
        except IndexError:
            pass

        return self._value(default)

    def implode(self, glue=',', key=None):
        first = self.first()
        if not isinstance(first, str) and key:
            return glue.join(self.pluck(key))
        return glue.join([str(x) for x in self])

    def is_empty(self):
        return not self

    def map(self, callback):
        self._check_is_callable(callback)
        items = [callback(x) for x in self]
        return self.__class__(items)

    def map_into(self, cls, method=None):
        results = []
        for item in self:

            if method:
                results.append(getattr(cls, method)(item))
            else:
                results.append(cls(item))

        return self.__class__(results)

    def merge(self, items):
        if not isinstance(items, list):
            raise ValueError('Unable to merge uncompatible types')

        if isinstance(items, Collection):
            items = items.all()

        self._items += items
        return self

    def pluck(self, attribute):
        attributes = []
        for item in self:
            for key, value in item.items():
                if key == attribute:
                    attributes.append(value)
        return attributes

    def pop(self):
        last = self._items.pop()
        return last

    def prepend(self, value):
        self._items.insert(0, value)
        return self

    def pull(self, key):
        value = self.get(key)
        self.forget(key)
        return value

    def push(self, value):
        self._items.append(value)

    def put(self, key, value):
        self[key] = value
        return self

    def reduce(self, callback, initial=0):
        return reduce(callback, self, initial)

    def reject(self, callback):
        self._check_is_callable(callback)

        items = self._get_value(callback) or self._items
        self._items = items

    def reverse(self):
        self._items = self[::-1]

    def serialize(self):
        pass

    def shift(self):
        return self.pull(0)

    def sort(self):
        self._items = sorted(self)

    def sum(self, key=None):
        result = 0
        items = self._get_value(key) or self._items
        try:
            result = sum(items)
        except TypeError:
            pass
        return result

    def to_json(self):
        # todo implements this methods
        pass

    def transform(self, callback):
        self._check_is_callable(callback)
        self._items = self._get_value(callback)

    def unique(self, key=None):
        if not key:
            items = list(set(self._items))
            return self.__class__(items)

        keys = set()
        items = []

        for item in self:
            if not item[key] in keys:
                items.append(item)
                keys.add(item[key])

        return self.__class__(items)

    def where(self, attribute, value):
        attributes = []
        for item in self:
            if item.get(attribute) == value:
                attributes.append(item)

        return attributes or None

    def zip(self, items):
        if isinstance(items, Collection):
            items = items.all()
        if not isinstance(items, list):
            raise ValueError("The 'items' parameter must be a list or a Collection")

        _items = []
        for x, y in zip(self, items):
            _items.append([x, y])
        return self.__class__(_items)

    def _get_value(self, key):
        if not key:
            return None

        items = []
        for item in self:
            if isinstance(key, str):
                if hasattr(item, key) or (key in item):
                    items.append(getattr(item, key, item[key]))
            elif callable(key):
                result = key(item)
                if result:
                    items.append(result)
        return items

    def _value(self, value):
        if callable(value):
            return value()
        return value

    def _check_is_callable(self, callback):
        if not callable(callback):
            raise ValueError("The 'callback' should be a function")
        return True

    def __iter__(self):
        for item in self._items:
            yield item

    def __eq__(self, other):
        if isinstance(other, Collection):
            return other == other.all()
        return other == self._items

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self._items[item])

        return self._items[item]

    def __setitem__(self, key, value):
        self._items[key] = value

    def __delitem__(self, key):
        del self._items[key]

    def __ne__(self, other):
        if isinstance(other, Collection):
            other = other.all()
        return other != self._items

    def __len__(self):
        return len(self._items)

    def __le__(self, other):
        if isinstance(other, Collection):
            other = other.all()
        return self._items <= other

    def __lt__(self, other):
        if isinstance(other, Collection):
            other = other.all()
        return self._items < other

    def __ge__(self, other):
        if isinstance(other, Collection):
            other = other.all()
        return self._items >= other

    def __gt__(self, other):
        if isinstance(other, Collection):
            other = other.all()
        return self._items > other
