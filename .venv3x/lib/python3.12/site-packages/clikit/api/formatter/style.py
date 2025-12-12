from typing import Optional


class Style(object):
    """
    A formatter style.
    """

    def __init__(self, tag=None):  # type: (Optional[str]) -> None
        self._tag = tag
        self._fg_color = None
        self._bg_color = None
        self._bold = False
        self._underlined = False
        self._italic = False
        self._dark = False
        self._blinking = False
        self._inverse = False
        self._hidden = False

    @property
    def tag(self):  # type: () -> Optional[str]
        return self._tag

    @property
    def foreground_color(self):  # type: () -> str
        return self._fg_color

    @property
    def background_color(self):  # type: () -> str
        return self._bg_color

    def fg(self, color):  # type: (str) -> Style
        """
        Sets the foreground color.
        """
        self._fg_color = color

        return self

    def bg(self, color):  # type: (str) -> Style
        """
        Sets the background color.
        """
        self._bg_color = color

        return self

    def bold(self, bold=True):  # type: (bool) -> Style
        """
        Sets or unsets the font weight to bold.
        """
        self._bold = bold

        return self

    def underlined(self, underlined=True):  # type: (bool) -> Style
        """
        Enables or disables underlining.
        """
        self._underlined = underlined

        return self

    def italic(self, italic=True):  # type: (bool) -> Style
        """
        Enables or disables italic
        """
        self._italic = italic

        return self

    def dark(self, dark=True):  # type: (bool) -> Style
        """
        Enables or disables dark
        """
        self._dark = dark

        return self

    def blinking(self, blinking=True):  # type: (bool) -> Style
        """
        Enables or disables blinking.
        """
        self._blinking = blinking

        return self

    def inverse(self, inverse=True):  # type: (bool) -> Style
        """
        Enables or disables inverse colors.
        """
        self._inverse = inverse

        return self

    def hidden(self, hidden=True):  # type: (bool) -> Style
        """
        Hides or shows the text.
        """
        self._hidden = hidden

        return self

    def is_bold(self):  # type: () -> bool
        return self._bold

    def is_underlined(self):  # type: () -> bool
        return self._underlined

    def is_italic(self):  # type: () -> bool
        return self._italic

    def is_dark(self):  # type: () -> bool
        return self._dark

    def is_blinking(self):  # type: () -> bool
        return self._blinking

    def is_inverse(self):  # type: () -> bool
        return self._inverse

    def is_hidden(self):  # type: () -> bool
        return self._hidden
