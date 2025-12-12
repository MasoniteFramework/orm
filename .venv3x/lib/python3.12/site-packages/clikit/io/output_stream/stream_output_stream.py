import io
import os
import platform
import sys

from clikit.api.io.output_stream import OutputStream


class StreamOutputStream(OutputStream):
    """
    An output stream that writes to a stream.
    """

    def __init__(self, stream):  # type: (io.TextIOWrapper) -> None
        self._stream = stream

    def write(self, string):  # type: (str) -> None
        """
        Writes a string to the stream.
        """
        if self.is_closed():
            raise io.UnsupportedOperation("Cannot write to a closed input.")

        self._stream.write(string)
        self._stream.flush()

    def flush(self):  # type: () -> None
        """
        Flushes the stream and forces all pending text to be written out.
        """
        if self.is_closed():
            raise io.UnsupportedOperation("Cannot write to a closed input.")

        self._stream.flush()

    def supports_ansi(self):  # type: () -> bool
        """
        Returns whether the stream supports ANSI format codes.
        """
        if platform.system().lower() == "windows":
            shell_supported = (
                os.getenv("ANSICON") is not None
                or "ON" == os.getenv("ConEmuANSI")
                or "xterm" == os.getenv("Term")
            )

            if shell_supported:
                return True

            if not hasattr(self._stream, "fileno"):
                return False

            # Checking for Windows version
            # If we have a compatible version
            # activate color support
            windows_version = sys.getwindowsversion()
            major, build = windows_version[0], windows_version[2]
            if (major, build) < (10, 14393):
                return False

            # Activate colors if possible
            import ctypes
            import ctypes.wintypes

            FILE_TYPE_CHAR = 0x0002
            FILE_TYPE_REMOTE = 0x8000
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

            kernel32 = ctypes.windll.kernel32

            fileno = self._stream.fileno()

            if fileno == 1:
                h = kernel32.GetStdHandle(-11)
            elif fileno == 2:
                h = kernel32.GetStdHandle(-12)
            else:
                return False

            if h is None or h == ctypes.wintypes.HANDLE(-1):
                return False

            if (kernel32.GetFileType(h) & ~FILE_TYPE_REMOTE) != FILE_TYPE_CHAR:
                return False

            mode = ctypes.wintypes.DWORD()
            if not kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                return False

            if (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING) == 0:
                kernel32.SetConsoleMode(
                    h, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                )
                return True

            return False

        if not hasattr(self._stream, "fileno"):
            return False

        try:
            return os.isatty(self._stream.fileno())
        except io.UnsupportedOperation:
            return False

    def close(self):  # type: () -> None
        """
        Closes the stream.
        """
        self._stream.close()

    def is_closed(self):  # type: () -> bool
        """
        Returns whether the stream is closed.
        """
        return self._stream.closed
