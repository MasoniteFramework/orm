from typing import Optional

from clikit.api.formatter import Formatter

from .input import Input
from .output import Output


class IO(Formatter):
    """
    Provides methods to access the console input and output.
    """

    def __init__(
        self, input, output, error_output
    ):  # type: (Input, Output, Output) -> None
        self._input = input
        self._output = output
        self._error_output = error_output
        self._terminal_dimensions = None

    @property
    def input(self):  # type: () -> Input
        return self._input

    @property
    def output(self):  # type: () -> Output
        return self._output

    @property
    def error_output(self):  # type: () -> Output
        return self._error_output

    def read(self, length, default=None):  # type: (int, Optional[str]) -> str
        """
        Reads the given amount of characters from the standard input.

        :raises: IOException
        """
        return self._input.read(length, default=default)

    def read_line(
        self, length=None, default=None
    ):  # type: (Optional[int], Optional[str]) -> str
        """
        Reads a line from the standard input.

        :raises: IOException
        """
        return self._input.read_line(length=length, default=default)

    def write(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a string to the standard output.

        The string is formatted before it is written to the output.
        """
        self._output.write(string, flags=flags)

    def write_line(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a line to the standard output.

        The string is formatted before it is written to the output.
        """
        self._output.write_line(string, flags=flags)

    def write_raw(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a string to the standard output without formatting.
        """
        self._output.write_raw(string, flags=flags)

    def write_line_raw(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a line to the standard output without formatting.
        """
        self._output.write_raw(string, flags=flags)

    def error(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a string to the error output.

        The string is formatted before it is written to the output.
        """
        self._error_output.write(string, flags=flags)

    def error_line(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a line to the error output.

        The string is formatted before it is written to the output.
        """
        self._error_output.write_line(string, flags=flags)

    def error_raw(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a string to the error output without formatting.
        """
        self._error_output.write_raw(string, flags=flags)

    def error_line_raw(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a line to the error output without formatting.
        """
        self._error_output.write_raw(string, flags=flags)

    def flush(self):  # type: () -> None
        """
        Flushes the outputs and forces all pending text to be written out.
        """
        self._output.flush()
        self._error_output.flush()

    def close(self):  # type: () -> None
        """
        Closes the input and the outputs.
        """
        self._input.close()
        self._output.close()
        self._error_output.close()

    def set_interactive(self, interactive):  # type: (bool) -> None
        """
        Enables or disables interaction with the user.
        """
        self._input.set_interactive(interactive)

    def is_interactive(self):  # type: () -> bool
        """
        Returns whether the user may be asked for input.
        """
        return self._input.is_interactive()

    def set_verbosity(self, verbosity):  # type: (int) -> None
        """
        Sets the verbosity of the output.
        """
        self._output.set_verbosity(verbosity)
        self._error_output.set_verbosity(verbosity)

    def is_verbose(self):  # type: () -> bool
        """
        Returns whether the verbosity is VERBOSE or greater.
        """
        return self._output.is_verbose()

    def is_very_verbose(self):  # type: () -> bool
        """
        Returns whether the verbosity is VERY_VERBOSE or greater.
        """
        return self._output.is_very_verbose()

    def is_debug(self):  # type: () -> bool
        """
        Returns whether the verbosity is DEBUG.
        """
        return self._output.is_debug()

    @property
    def verbosity(self):  # type: () -> int
        return self._output.verbosity

    def set_quiet(self, quiet):  # type: (bool) -> None
        """
        Sets whether all output should be suppressed.
        """
        self._output.set_quiet(quiet)
        self._error_output.set_quiet(quiet)

    def is_quiet(self):  # type: () -> bool
        """
        Returns whether all output is suppressed.
        """
        return self._output.is_quiet()

    def set_terminal_dimensions(self, dimensions):  # type: (Rectangle) -> None
        """
        Sets the dimensions of the terminal.
        """
        self._terminal_dimensions = dimensions

    @property
    def terminal_dimensions(self):  # type: () -> Rectangle
        if not self._terminal_dimensions:
            self._terminal_dimensions = self.get_default_terminal_dimensions()

        return self._terminal_dimensions

    def get_default_terminal_dimensions(self):  # type: () -> Rectangle
        """
        Returns the default terminal dimensions.
        """
        from clikit.ui.rectangle import Rectangle

        return Rectangle(80, 20)

    def set_formatter(self, formatter):  # type: (Formatter) -> None
        """
        Sets the output formatter.
        """
        self._output.set_formatter(formatter)
        self._error_output.set_formatter(formatter)

    def supports_ansi(self):  # type: () -> bool
        return self._output.supports_ansi()

    @property
    def formatter(self):  # type: () -> Formatter
        """
        Returns the output formatter.
        """
        return self._output.formatter

    def format(self, string, style=None):  # type: (str, Style) -> str
        """
        Formats the given string.
        """
        return self._output.formatter.format(string, style=style)

    def remove_format(self, string):  # type: (str) -> str
        """
        Removes the format tags from the given string.
        """
        return self._output.formatter.remove_format(string)

    def section(self):
        return self.__class__(
            self._input, self._output.section(), self._error_output.section()
        )
