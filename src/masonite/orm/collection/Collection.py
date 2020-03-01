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
        pass

    def map(self):
        pass

    def merge(self):
        pass

    def pluck(self):
        pass

    def pop(self):
        pass

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

    def sum(self):
        pass

    def to_json(self):
        pass

    def transform(self):
        pass

    def unique(self):
        pass

    def where(self):
        pass

    def zip(self):
        pass
