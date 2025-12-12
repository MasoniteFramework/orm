from typing import Optional


from clikit.api.formatter import Formatter
from clikit.api.io import IO
from clikit.api.io import Input
from clikit.api.io import Output
from clikit.formatter import PlainFormatter

from .input_stream import StringInputStream
from .output_stream import BufferedOutputStream


class BufferedIO(IO):
    """
    An I/O that reads from and writes to a buffer.
    """

    def __init__(
        self, input_data="", formatter=None
    ):  # type: (str, Optional[Formatter]) -> None
        if formatter is None:
            formatter = PlainFormatter()

        input = Input(StringInputStream(input_data))
        output = Output(BufferedOutputStream(), formatter)
        error_output = Output(BufferedOutputStream(), formatter)

        super(BufferedIO, self).__init__(input, output, error_output)

    def set_input(self, data):  # type: (str) -> None
        self.input.stream.set(data)

    def append_input(self, data):  # type: (str) -> None
        self.input.stream.append(data)

    def clear_input(self):  # type: () -> None
        self.input.stream.clear()

    def fetch_output(self):  # type: () -> str
        return self.output.stream.fetch()

    def clear_output(self):  # type: () -> None
        self.output.stream.clear()

    def fetch_error(self):  # type: () -> str
        return self.error_output.stream.fetch()

    def clear_error(self):  # type: () -> None
        self.error_output.stream.clear()

    def section(self):
        io = self.__class__()
        io._input = self._input
        io._output = self._output.section()
        io._error_output = self._error_output.section()

        return io
