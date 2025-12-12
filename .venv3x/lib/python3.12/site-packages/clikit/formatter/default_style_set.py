from clikit.api.formatter import Style
from clikit.api.formatter import StyleSet


class DefaultStyleSet(StyleSet):
    """
    The Default TTY style set
    """

    def __init__(self):  # type: () -> None
        styles = [
            Style("info").fg("green"),
            Style("comment").fg("cyan"),
            Style("question").fg("blue"),
            Style("error").fg("red").bold(),
            Style("b").bold(),
            Style("u").underlined(),
            Style("c1").fg("cyan"),
            Style("c2").fg("yellow"),
        ]

        super(DefaultStyleSet, self).__init__(styles)
