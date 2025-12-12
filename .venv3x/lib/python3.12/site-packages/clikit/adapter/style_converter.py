from pastel.style import Style as PastelStyle

from clikit.api.formatter import Style


class StyleConverter(object):
    """
    Converts a TTY Style instance to a Pastel Style instance.
    """

    @classmethod
    def convert(cls, style):  # type: (Style) -> PastelStyle
        options = []

        if style.is_bold():
            options.append("bold")

        if style.is_italic():
            options.append("italic")

        if style.is_dark():
            options.append("dark")

        if style.is_underlined():
            options.append("underline")

        if style.is_blinking():
            options.append("blink")

        if style.is_inverse():
            options.append("reverse")

        if style.is_hidden():
            options.append("conceal")

        return PastelStyle(style.foreground_color, style.background_color, options)
