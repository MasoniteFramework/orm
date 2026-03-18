from .BasePaginator import BasePaginator


class SimplePaginator(BasePaginator):
    def __init__(self, result, per_page, current_page, url=None):
        self.result = result
        self.current_page = current_page
        self.per_page = per_page
        self.count = len(self.result)
        self.next_page = (int(self.current_page) + 1) if self.has_more_pages() else None
        self.previous_page = (int(self.current_page) - 1) or None
        self.url = url

    def serialize(self, *args, **kwargs):
        return {
            "data": self.result.serialize(*args, **kwargs),
            "meta": {
                "next_page": self.next_page,
                "count": self.count,
                "previous_page": self.previous_page,
                "current_page": self.current_page,
            },
        }

    def has_more_pages(self):
        return len(self.result) > self.per_page
