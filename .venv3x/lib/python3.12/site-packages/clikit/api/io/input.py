from typing import Optional

from .input_stream import InputStream


class Input(object):
    """
    The console input.

    This class wraps an input stream and adds convenience functionality for
    reading that stream.
    """

    def __init__(self, stream):  # type: (InputStream) -> None
        self._stream = stream
        self._interactive = True

    def read(self, length, default=None):  # type: (int, Optional[str]) -> str
        """
        Reads the given amount of characters from the input stream.

        :raises: IOException
        """
        if not self._interactive:
            return default

        return self._stream.read(length)

    def read_line(
        self, length=None, default=None
    ):  # type: (Optional[int], Optional[str]) -> str
        """
        Reads a line from the input stream.

        :raises: IOException
        """
        if not self._interactive:
            return default

        return self._stream.read_line(length=length)

    def close(self):  # type: () -> None
        """
        Closes the input.
        """
        self._stream.close()

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the input is closed.
        """
        return self._stream.is_closed()

    def set_stream(self, stream):  # type: (InputStream) -> None
        """
        Sets the underlying stream.
        """
        self._stream = stream

    @property
    def stream(self):  # type: () -> InputStream
        return self._stream

    def set_interactive(self, interactive):  # type: (bool) -> None
        """
        Enables or disables interaction with the user.
        """
        self._interactive = interactive

    def is_interactive(self):  # type: () -> bool
        """
        Returns whether the user may be asked for input.
        """
        return self._interactive
