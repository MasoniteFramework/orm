from clikit.api.application import Application
from clikit.api.args.format import ArgsFormat
from clikit.api.args.format import ArgsFormatBuilder
from clikit.api.args.format import Argument
from clikit.api.command import Command
from clikit.api.command import CommandCollection
from clikit.ui.components import EmptyLine
from clikit.ui.components import LabeledParagraph
from clikit.ui.components import NameVersion
from clikit.ui.components import Paragraph
from clikit.ui.layout import BlockLayout

from .abstract_help import AbstractHelp


class ApplicationHelp(AbstractHelp):
    """
    Renders the help of a console application.
    """

    def __init__(self, application):  # type: (Application) -> None
        self._application = application

    def _render_help(self, layout):  # type: (BlockLayout) -> None
        help = self._application.config.help
        commands = self._application.named_commands
        global_args_format = self._application.global_args_format

        builder = ArgsFormatBuilder()
        builder.add_argument(
            Argument("command", Argument.REQUIRED, "The command to execute")
        )
        builder.add_argument(
            Argument("arg", Argument.MULTI_VALUED, "The arguments of the command")
        )
        builder.add_options(*global_args_format.get_options().values())

        args_format = builder.format

        self._render_name(layout, self._application)
        self._render_usage(layout, self._application, args_format)
        self._render_arguments(layout, args_format.get_arguments().values())

        if args_format.has_options():
            self._render_global_options(layout, args_format.get_options().values())

        if not commands.is_empty():
            self._render_commands(layout, commands)

        if help:
            self._render_description(layout, help)

    def _render_name(
        self, layout, application
    ):  # type: (BlockLayout, Application) -> None
        layout.add(NameVersion(application.config))
        layout.add(EmptyLine())

    def _render_usage(
        self, layout, application, args_format
    ):  # type: (BlockLayout, Application, ArgsFormat) -> None
        app_name = application.config.name

        layout.add(Paragraph("<b>USAGE</b>"))

        with layout.block():
            self._render_synopsis(layout, args_format, app_name)

        layout.add(EmptyLine())

    def _render_commands(
        self, layout, commands
    ):  # type: (BlockLayout, CommandCollection) -> None
        layout.add(Paragraph("<b>AVAILABLE COMMANDS</b>"))

        with layout.block():
            for command in sorted(commands, key=lambda c: c.name):
                self._render_command(layout, command)

        layout.add(EmptyLine())

    def _render_command(self, layout, command):  # type: (BlockLayout, Command) -> None
        if command.config.is_hidden():
            return

        description = command.config.description
        name = "<c1>{}</c1>".format(command.name)

        layout.add(LabeledParagraph(name, description))

    def _render_description(self, layout, help):  # type: (BlockLayout, str) -> None
        help = help.format(script_name=self._application.config.name or "console")

        layout.add(Paragraph("<b>DESCRIPTION</b>"))
        with layout.block():
            for paragraph in help.split("\n"):
                layout.add(Paragraph(paragraph))

        layout.add(EmptyLine())
