import sys

from .stream_output_stream import StreamOutputStream


class ErrorOutputStream(StreamOutputStream):
    """
    An output stream that writes to the error output.
    """

    def __init__(self):  # type: () -> None
        super(ErrorOutputStream, self).__init__(sys.stderr)
