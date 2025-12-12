from typing import Optional


class InputStream(object):
    """
    The console input stream.
    """

    def read(self, length):  # type: (int) -> str
        """
        Reads the given amount of characters from the stream.
        """
        raise NotImplementedError()

    def read_line(self, length=None):  # type: (Optional[int]) -> str
        """
        Reads a line from the stream.
        """
        raise NotImplementedError()

    def close(self):  # type: () -> None
        """
        Closes the stream
        """
        raise NotImplementedError()

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the stream is closed or not
        """
        raise NotImplementedError()
