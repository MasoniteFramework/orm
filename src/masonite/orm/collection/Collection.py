class Collection:
    def __init__(self, items=[]):
        self.items = items

    def take(self, number):
        return self.items[:number]

    def first(self):
        return self.items[0]

    def last(self):
        return self.items[-1]

    def all(self):
        return self.items

    def __len__(self):
        return len(self.items)

    def avg(self):
        pass

    def chunk(self):
        pass

    def collapse(self):
        pass

    def contains(self):
        pass

    def count(self):
        pass

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
        pass

    def implode(self):
        pass

    def is_empty(self):
        return True if not self.items else False

    def map(self):
        pass

    def merge(self):
        pass

    def pluck(self, attribute):
        attributes = []
        for item in self.items:
            for key, value in item.items():
                if key == attribute:
                    attributes.append(value)
        return attributes

    def pop(self):
        last = self.items.pop()
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
        items = self._value_retriever(key)
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
        for item in self.items:
            if item.get(attribute) == value:
                attributes.append(item)

        return attributes or None

    def zip(self):
        pass

    def _value_retriever(self, key):
        items = []
        for item in self.items:
            if not key:
                items = self.items
                break
            elif isinstance(key, str):
                if hasattr(item, key) or (key in item):
                    items.append(getattr(item, key, item[key]))
            elif callable(key):
                items.append(key(item))
        return items
