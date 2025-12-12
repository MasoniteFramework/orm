class Formatter(object):
    """
    Formats strings.
    """

    def format(self, string, style=None):  # type: (str, Style) -> str
        """
        Formats the given string.
        """
        raise NotImplementedError()

    def remove_format(self, string):  # type: (str) -> str
        """
        Removes the format tags from the given string.
        """
        raise NotImplementedError()

    def disable_ansi(self):  # type: () -> bool
        raise NotImplementedError()

    def force_ansi(self):  # type: () -> bool
        raise NotImplementedError()

    def add_style(self, style):  # type: (Style) -> None
        raise NotImplementedError()
