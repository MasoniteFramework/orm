import os

from typing import Optional

from clikit.api.formatter import Formatter
from clikit.formatter import NullFormatter
from clikit.utils._compat import to_str

from .flags import DEBUG
from .flags import NORMAL
from .flags import VERBOSE
from .flags import VERY_VERBOSE
from .output_stream import OutputStream


class Output(Formatter):
    """
    The console output.

    This class wraps an output stream and adds convenience functionality for
    writing that stream.
    """

    def __init__(
        self, stream, formatter=None
    ):  # type: (OutputStream, Optional[Formatter]) -> None
        self._stream = stream

        if formatter is None:
            formatter = NullFormatter()

        self._formatter = formatter
        self._quiet = False

        self._format_output = (
            self._stream.supports_ansi()
            and not formatter.disable_ansi()
            or formatter.force_ansi()
        )

        self._verbosity = 0
        self._section_outputs = []

    def write(
        self, string, flags=None, new_line=False
    ):  # type: (str, Optional[int], bool) -> None
        """
        Writes a string to the output stream.

        The string is formatted before it is written to the output stream.
        """
        if self._may_write(flags):
            if self._format_output:
                formatted = self.format(string)
            else:
                formatted = self.remove_format(string)

            if new_line:
                formatted += "\n"

            self._stream.write(to_str(formatted))

    def write_line(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a line of text to the output stream.

        The string is formatted before it is written to the output stream.
        """
        self.write(string, flags=flags, new_line=True)

    def write_raw(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a string to the output stream without formatting.
        """
        if self._may_write(flags):
            self._stream.write(to_str(string))

    def write_line_raw(self, string, flags=None):  # type: (str, Optional[int]) -> None
        """
        Writes a string to the output stream without formatting.
        """
        if self._may_write(flags):
            self._stream.write(to_str(string.rstrip("\n") + "\n"))

    def flush(self):  # type: () -> None
        """
        Forces all pending text to be written out.
        """
        self._stream.flush()

    def close(self):  # type: () -> None
        """
        Closes the output.
        """
        self._stream.close()

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the output is closed.
        """
        return self._stream.is_closed()

    def set_stream(self, stream):  # type: (OutputStream) -> None
        """
        Sets the underlying stream.
        """
        self._stream = stream

        if self._formatter.force_ansi():
            self._format_output = True
        else:
            self._format_output = self._stream.supports_ansi()

    @property
    def stream(self):  # type: () -> OutputStream
        """
        Returns the underlying stream.
        """
        return self._stream

    def set_formatter(self, formatter):  # type: (Formatter) -> None
        """
        Sets the underlying formatter.
        """
        self._formatter = formatter

        if formatter.force_ansi():
            self._format_output = True
        else:
            self._format_output = self._stream.supports_ansi()

    @property
    def formatter(self):  # type: () -> Formatter
        """
        Returns the underlying formatter.
        """
        return self._formatter

    def set_verbosity(self, verbosity):  # type: (int) -> None
        """
        Sets the verbosity level of the output.
        """
        if verbosity not in {NORMAL, VERBOSE, VERY_VERBOSE, DEBUG}:
            raise ValueError(
                "The verbosity must be one of NORMAL, VERBOSE, VERY_VERBOSE or DEBUG."
            )

        self._verbosity = verbosity

    @property
    def verbosity(self):  # type: () -> int
        """
        Returns the current verbosity level.
        """
        return self._verbosity

    def is_verbose(self):  # type: () -> bool
        """
        Returns whether the verbosity is VERBOSE or greater.
        """
        return self._verbosity >= VERBOSE

    def is_very_verbose(self):  # type: () -> bool
        """
        Returns whether the verbosity is VERY_VERBOSE or greater.
        """
        return self._verbosity >= VERY_VERBOSE

    def is_debug(self):  # type: () -> bool
        """
        Returns whether the verbosity is DEBUG.
        """
        return self._verbosity == DEBUG

    def set_quiet(self, quiet):  # type: (bool) -> None
        """
        Sets whether all output should be suppressed.
        """
        self._quiet = quiet

    def is_quiet(self):  # type: () -> bool
        """
        Returns whether all output is suppressed.
        """
        return self._quiet

    def format(self, string, style=None):  # type: (str, Style) -> str
        """
        Formats the given string.
        """
        return self._formatter.format(string, style)

    def remove_format(self, string):  # type: (str) -> str
        """
        Removes the format tags from the given string.
        """
        return self._formatter.remove_format(string)

    def supports_ansi(self):  # type: () -> bool
        return self._format_output

    def section(self):  # type: (SectionOutput) -> SectionOutput
        from .section_output import SectionOutput

        return SectionOutput(self._stream, self._section_outputs, self._formatter)

    def _may_write(self, flags):  # type: (int) -> bool
        """
        Returns whether an output may be written for the given flags.
        """
        if flags is None:
            flags = 0

        if self._quiet:
            return False

        if flags & VERBOSE:
            return self._verbosity >= VERBOSE

        if flags & VERY_VERBOSE:
            return self._verbosity >= VERY_VERBOSE

        if flags & DEBUG:
            return self._verbosity >= DEBUG

        return True
