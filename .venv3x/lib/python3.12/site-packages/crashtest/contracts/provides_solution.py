from .solution import Solution


class ProvidesSolution:
    @property
    def solution(self) -> Solution:
        raise NotImplementedError()
