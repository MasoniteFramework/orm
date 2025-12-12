from io import BytesIO
from io import SEEK_END

from clikit.utils._compat import encode

from .stream_input_stream import StreamInputStream


class StringInputStream(StreamInputStream):
    """
    An input stream that reads from a string.
    """

    def __init__(self, string=""):  # type: (str) -> None
        self._stream = BytesIO()

        super(StringInputStream, self).__init__(self._stream)

        self.set(string)

    def clear(self):  # type: () -> None
        self._stream.truncate(0)
        self._stream.seek(0)

    def set(self, string):  # type: (str) -> None
        self.clear()

        self._stream.write(encode(string))
        self._stream.seek(0)

    def append(self, string):  # type: (str) -> None
        pos = self._stream.tell()
        self._stream.seek(0, SEEK_END)
        self._stream.write(encode(string))
        self._stream.seek(pos)
