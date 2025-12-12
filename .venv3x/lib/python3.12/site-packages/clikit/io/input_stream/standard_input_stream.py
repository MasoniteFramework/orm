import sys

from .stream_input_stream import StreamInputStream


class StandardInputStream(StreamInputStream):
    """
    An input stream that reads from the standard input.
    """

    def __init__(self):  # type: () -> None
        super(StandardInputStream, self).__init__(sys.stdin)
