from typing import Optional

from clikit.api.io.input_stream import InputStream


class NullInputStream(InputStream):
    """
    An input stream that returns nothing.
    """

    def read(self, length):  # type: (int) -> str
        """
        Reads the given amount of characters from the stream.
        """
        return ""

    def read_line(self, length=None):  # type: (Optional[int]) -> str
        """
        Reads a line from the stream.
        """
        return ""

    def close(self):  # type: () -> None
        """
        Closes the stream
        """

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the stream is closed or not
        """
        return False
