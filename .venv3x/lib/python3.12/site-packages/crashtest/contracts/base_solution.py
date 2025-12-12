from typing import List

from .solution import Solution


class BaseSolution(Solution):
    def __init__(self, title: str = None, description: str = None) -> None:
        self._title = title
        self._description = description
        self._links = []

    @property
    def solution_title(self) -> str:
        return self._title

    @property
    def solution_description(self) -> str:
        return self._description

    @property
    def documentation_links(self) -> List[str]:
        return self._links
