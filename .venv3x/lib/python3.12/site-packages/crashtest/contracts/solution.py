from typing import List


class Solution:
    @property
    def solution_title(self) -> str:
        raise NotImplementedError()

    @property
    def solution_description(self) -> str:
        raise NotImplementedError()

    @property
    def documentation_links(self) -> List[str]:
        raise NotImplementedError()
