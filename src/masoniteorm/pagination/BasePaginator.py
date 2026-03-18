import json


class BasePaginator:
    def __iter__(self):
        yield from self.result

    def to_json(self):
        return json.dumps(self.serialize())
