from typing import List
from typing import Type

from .solution import Solution


class SolutionProviderRepository:
    def register_solution_provider(
        self, solution_provider_class: Type
    ) -> "SolutionProviderRepository":
        raise NotImplementedError()

    def register_solution_providers(
        self, solution_provider_classes: List[Type]
    ) -> "SolutionProviderRepository":
        raise NotImplementedError()

    def get_solutions_for_exception(self, exception: Exception) -> List[Solution]:
        raise NotImplementedError()
