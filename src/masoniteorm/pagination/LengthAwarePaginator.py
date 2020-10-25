import math
from .BasePaginator import BasePaginator


class LengthAwarePaginator(BasePaginator):
    def __init__(self, result, per_page, current_page, total, url=None):
        self.result = result
        self.current_page = current_page
        self.per_page = per_page
        self.count = len(self.result)
        self.last_page = int(math.ceil(total / per_page))
        self.next_page = (int(self.current_page) + 1) if self.has_more_pages() else None
        self.previous_page = (int(self.current_page) - 1) or None
        self.total = total
        self.url = url

    def serialize(self):
        return {
            "data": self.result.serialize(),
            "meta": {
                "total": self.total,
                "next_page": self.next_page,
                "count": self.count,
                "previous_page": self.previous_page,
                "last_page": self.last_page,
                "current_page": self.current_page,
            },
        }

    def has_more_pages(self):
        return self.current_page < self.last_page
