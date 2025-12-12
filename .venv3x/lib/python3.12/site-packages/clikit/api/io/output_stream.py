class OutputStream(object):
    """
    The console output stream.
    """

    def write(self, string):  # type: (str) -> None
        """
        Writes a string to the stream.
        """
        raise NotImplementedError()

    def flush(self):  # type: () -> None
        """
        Flushes the stream and forces all pending text to be written out.
        """
        raise NotImplementedError()

    def supports_ansi(self):  # type: () -> bool
        """
        Returns whether the stream supports ANSI format codes.
        """
        raise NotImplementedError()

    def close(self):  # type: () -> None
        """
        Closes the stream.
        """
        raise NotImplementedError()

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the stream is closed.
        """
        raise NotImplementedError()
