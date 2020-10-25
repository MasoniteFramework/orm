import json


class BasePaginator:
    def __iter__(self):
        for result in self.result:
            yield result

    def to_json(self):
        return json.dumps(self.serialize())
