from typing import List

from .solution import Solution


class HasSolutionsForException:
    def can_solve(self, exception: Exception) -> bool:
        raise NotImplementedError()

    def get_solutions(self, exception: Exception) -> List[Solution]:
        raise NotImplementedError()
