import sys

from .stream_output_stream import StreamOutputStream


class StandardOutputStream(StreamOutputStream):
    """
    An output stream that writes to the standard output.
    """

    def __init__(self):  # type: () -> None
        super(StandardOutputStream, self).__init__(sys.stdout)
