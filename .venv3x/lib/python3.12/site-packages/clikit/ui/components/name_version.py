from clikit.api.io import IO
from clikit.api.config import ApplicationConfig
from clikit.ui import Component

from .paragraph import Paragraph


class NameVersion(Component):
    """
    Renders the name and version of an application.
    """

    def __init__(self, config):  # type: (ApplicationConfig) -> None
        self._config = config

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        if self._config.display_name and self._config.version:
            paragraph = Paragraph(
                "{} version <c1>{}</c1>".format(
                    self._config.display_name, self._config.version
                )
            )
        elif self._config.display_name:
            paragraph = Paragraph("{}".format(self._config.display_name))
        else:
            paragraph = Paragraph("Console Tool")

        paragraph.render(io, indentation)
