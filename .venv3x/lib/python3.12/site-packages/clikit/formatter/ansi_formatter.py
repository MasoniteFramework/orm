from typing import Optional

from pastel import Pastel

from clikit.adapter.style_converter import StyleConverter
from clikit.api.formatter import Formatter
from clikit.api.formatter import Style
from clikit.api.formatter import StyleSet

from .default_style_set import DefaultStyleSet


class AnsiFormatter(Formatter):
    """
    A formatter that replaces style tags by ANSI format codes.
    """

    def __init__(self, style_set=None, forced=False):  # type: (StyleSet) -> None
        self._formatter = Pastel(True)
        self._forced = forced

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
        if style is not None:
            self._formatter._style_stack.push(StyleConverter.convert(style))

        formatted = self._formatter.colorize(string)

        if style is not None:
            self._formatter._style_stack.pop()

        return formatted

    def remove_format(self, string):  # type: (str) -> str
        with self._formatter.colorized(False):
            return self._formatter.colorize(string)

    def disable_ansi(self):  # type: () -> bool
        return False

    def force_ansi(self):  # type: () -> bool
        return self._forced

    def add_style(self, style):  # type: (Style) -> None
        pastel_style = StyleConverter.convert(style)

        self._formatter.add_style(
            style.tag,
            pastel_style.foreground,
            pastel_style.background,
            pastel_style.options,
        )
