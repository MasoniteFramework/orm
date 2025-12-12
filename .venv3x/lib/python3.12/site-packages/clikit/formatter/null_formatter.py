from typing import Optional

from clikit.api.formatter import Formatter


class NullFormatter(Formatter):
    """
    A formatter that returns all text unchanged.
    """

    def format(self, string, style=None):  # type: (str, Optional[Style]) -> str
        return string

    def remove_format(self, string):  # type: (str) -> str
        return string

    def force_ansi(self):  # type: () -> bool
        return False

    def add_style(self, style):  # type: (Style) -> None
        pass
