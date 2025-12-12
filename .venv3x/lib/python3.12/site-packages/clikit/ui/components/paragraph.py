import re
import textwrap

from clikit.api.io import IO
from clikit.ui import Component


class Paragraph(Component):
    """
    A paragraph of text.

    The paragraph is wrapped into the dimensions of the output.
    """

    def __init__(self, text):  # type: (str) -> None
        self._text = text

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        line_prefix = " " * indentation
        text_width = io.terminal_dimensions.width - 1 - indentation

        text = re.sub(
            r"\n(?!\n)",
            "\n" + line_prefix,
            "\n".join(textwrap.wrap(self._text, text_width)),
        )

        io.write(line_prefix + text.rstrip() + "\n")
