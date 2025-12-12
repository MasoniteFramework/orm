from clikit.api.io.output_stream import OutputStream


class NullOutputStream(OutputStream):
    """
    An output stream that ignores all output.
    """

    def write(self, string):  # type: (str) -> None
        """
        Writes a string to the stream.
        """

    def flush(self):  # type: () -> None
        """
        Flushes the stream and forces all pending text to be written out.
        """

    def supports_ansi(self):  # type: () -> bool
        """
        Returns whether the stream supports ANSI format codes.
        """
        return False

    def close(self):  # type: () -> None
        """
        Closes the stream.
        """

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the stream is closed.
        """
        return False
