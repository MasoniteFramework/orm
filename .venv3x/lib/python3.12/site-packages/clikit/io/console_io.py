from typing import Optional

from clikit.api.io import IO
from clikit.api.io import Input
from clikit.api.io import Output
from clikit.formatter import AnsiFormatter
from clikit.formatter import PlainFormatter
from clikit.utils.terminal import Terminal
from clikit.ui.rectangle import Rectangle

from .input_stream import StandardInputStream
from .output_stream import ErrorOutputStream
from .output_stream import StandardOutputStream


class ConsoleIO(IO):
    """
    An I/O that reads from/prints to the console.
    """

    def __init__(
        self, input=None, output=None, error_output=None
    ):  # type: (Optional[Input], Optional[Output], Optional[Output]) -> None
        if input is None:
            input_stream = StandardInputStream()
            input = Input(input_stream)

        if output is None:
            output_stream = StandardOutputStream()
            if output_stream.supports_ansi():
                formatter = AnsiFormatter()
            else:
                formatter = PlainFormatter()

            output = Output(output_stream, formatter)

        if error_output is None:
            error_stream = ErrorOutputStream()
            if error_stream.supports_ansi():
                formatter = AnsiFormatter()
            else:
                formatter = PlainFormatter()

            error_output = Output(error_stream, formatter)

        super(ConsoleIO, self).__init__(input, output, error_output)

    def get_default_terminal_dimensions(self):  # type: () -> Rectangle
        terminal = Terminal()

        return Rectangle(terminal.width, terminal.height)
