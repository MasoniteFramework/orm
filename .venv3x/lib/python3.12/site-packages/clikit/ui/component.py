from clikit.api.io import IO


class Component(object):
    """
    A UI component that can be rendered on the I/O.
    """

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        raise NotImplementedError()
