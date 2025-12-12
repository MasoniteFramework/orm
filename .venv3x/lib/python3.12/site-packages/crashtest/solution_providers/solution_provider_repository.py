from typing import List
from typing import Optional
from typing import Type

from crashtest.contracts.has_solutions_for_exception import HasSolutionsForException
from crashtest.contracts.provides_solution import ProvidesSolution
from crashtest.contracts.solution import Solution
from crashtest.contracts.solution_provider_repository import (
    SolutionProviderRepository as BaseSolutionProviderRepository,
)


class SolutionProviderRepository(BaseSolutionProviderRepository):
    def __init__(self, solution_providers: Optional[List[Type]] = None) -> None:
        self._solution_providers = []

        if solution_providers is None:
            solution_providers = []

        self.register_solution_providers(solution_providers)

    def register_solution_provider(
        self, solution_provider_class: Type
    ) -> "SolutionProviderRepository":
        self._solution_providers.append(solution_provider_class)

        return self

    def register_solution_providers(
        self, solution_provider_classes: List[Type]
    ) -> "SolutionProviderRepository":
        for solution_provider_class in solution_provider_classes:
            self.register_solution_provider(solution_provider_class)

        return self

    def get_solutions_for_exception(self, exception: Exception) -> List[Solution]:
        solutions = []

        if isinstance(exception, Solution):
            solutions.append(exception)

        if isinstance(exception, ProvidesSolution):
            solutions.append(exception.solution)

        for solution_provider_class in self._solution_providers:
            if not issubclass(solution_provider_class, HasSolutionsForException):
                continue

            solution_provider: HasSolutionsForException = solution_provider_class()

            try:
                if not solution_provider.can_solve(exception):
                    continue
            except Exception:
                continue

            try:
                for solution in solution_provider.get_solutions(exception):
                    solutions.append(solution)
            except Exception:
                continue

        return solutions
