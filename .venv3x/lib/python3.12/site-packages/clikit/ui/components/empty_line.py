from clikit.api.io import IO
from clikit.ui import Component


class EmptyLine(Component):
    """
    An empty line.
    """

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        io.write("\n")
