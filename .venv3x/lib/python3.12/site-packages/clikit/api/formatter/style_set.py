from typing import Dict
from typing import List
from typing import Optional

from .style import Style


class StyleSet(object):
    """
    A set of styles used by the formatter.
    """

    def __init__(self, styles=None):  # type: (Optional[List[Style]]) -> None
        if styles is None:
            styles = []

        self._styles = {}

        for style in styles:
            self.add(style)

    @property
    def styles(self):  # type: () -> (Dict[str, Style])
        return self._styles

    def add(self, style):  # type: (Style) -> None
        if not style.tag:
            raise ValueError("The tag of a style added to the style set must be set.")

        self._styles[style.tag] = style

    def replace(self, styles):  # type: (Optional[List[Style]]) -> None
        self._styles = {}

        for style in styles:
            self.add(style)

    def remove(self, tag):  # type: (str) -> None
        if tag in self._styles:
            del self._styles[tag]
