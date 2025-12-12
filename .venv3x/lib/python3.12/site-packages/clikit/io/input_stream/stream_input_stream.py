import io

from typing import Optional

from clikit.api.io.input_stream import InputStream


class StreamInputStream(InputStream):
    """
    An input stream that reads from a stream.
    """

    def __init__(self, stream):  # type: (io.TextIOWrapper) -> None
        self._stream = stream

        if hasattr("stream", "seekable") and stream.seekable():
            stream.seek(0)

    def read(self, length):  # type: (int) -> str
        """
        Reads the given amount of characters from the stream.
        """
        if self.is_closed():
            raise io.UnsupportedOperation("Cannot read from a closed input.")

        try:
            data = self._stream.read(length)
        except EOFError:
            return ""

        if data:
            return data

        return ""

    def read_line(self, length=None):  # type: (Optional[int]) -> str
        """
        Reads a line from the stream.
        """
        if self.is_closed():
            raise io.UnsupportedOperation("Cannot read from a closed input.")

        try:
            return self._stream.readline(length) or ""
        except EOFError:
            return ""

    def close(self):  # type: () -> None
        """
        Closes the stream
        """
        self._stream.close()

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the stream is closed or not
        """
        return self._stream.closed
