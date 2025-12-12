from typing import Optional

from pastel import Pastel

from clikit.adapter.style_converter import StyleConverter
from clikit.api.formatter import Formatter
from clikit.api.formatter import Style
from clikit.api.formatter import StyleSet

from .default_style_set import DefaultStyleSet


class PlainFormatter(Formatter):
    """
    A formatter that removes all format tags.
    """

    def __init__(self, style_set=None):  # type: (StyleSet) -> None
        self._formatter = Pastel(False)

        if style_set is None:
            style_set = DefaultStyleSet()

        for tag, style in style_set.styles.items():
            pastel_style = StyleConverter.convert(style)

            self._formatter.add_style(
                tag,
                pastel_style.foreground,
                pastel_style.background,
                pastel_style.options,
            )

    def format(self, string, style=None):  # type: (str, Optional[Style]) -> str
        return self._formatter.colorize(string)

    def remove_format(self, string):  # type: (str) -> str
        return self._formatter.colorize(string)

    def disable_ansi(self):  # type: () -> bool
        return True

    def force_ansi(self):  # type: () -> bool
        return False

    def add_style(self, style):  # type: (Style) -> None
        pastel_style = StyleConverter.convert(style)

        self._formatter.add_style(
            style.tag,
            pastel_style.foreground,
            pastel_style.background,
            pastel_style.options,
        )
