from typing import Iterable

from clikit.api.args.format import Argument
from clikit.api.args.format import Option
from clikit.api.command import Command
from clikit.api.command import CommandCollection
from clikit.ui.components import EmptyLine
from clikit.ui.components import Paragraph
from clikit.ui.layout import BlockLayout

from .abstract_help import AbstractHelp


class CommandHelp(AbstractHelp):
    """
    Renders the help of a command.
    """

    def __init__(self, command):  # type: (Command) -> None
        self._command = command

    def _render_help(self, layout):  # type: (BlockLayout) -> None
        help = self._command.config.help
        args_format = self._command.args_format
        sub_commands = self._command.named_sub_commands

        self._render_usage(layout, self._command)

        if args_format.has_arguments():
            self._render_arguments(layout, args_format.get_arguments().values())

        if not sub_commands.is_empty():
            self._render_sub_commands(layout, sub_commands)

        if args_format.has_options(False):
            self._render_options(layout, args_format.get_options(False).values())

        if args_format.base_format and args_format.base_format.has_options():
            self._render_global_options(
                layout, args_format.base_format.get_options().values()
            )

        if help:
            self._render_description(layout, help)

    def _render_usage(self, layout, command):  # type: (BlockLayout, Command) -> None
        formats_to_print = []

        # Start with the default commands
        if command.has_default_sub_commands():
            # If the command has default commands, print them
            for sub_command in command.default_sub_commands:
                # The name of the sub command is only optional (i.e. printed
                # wrapped in brackets: "[sub]") if the command is not
                # anonymous
                name_optional = not sub_command.config.is_anonymous()

                formats_to_print.append((sub_command.args_format, name_optional))
        else:
            # Otherwise print the command's usage itself
            formats_to_print.append((command.args_format, False))

        # Add remaining sub-commands
        for sub_command in command.sub_commands:
            if sub_command.config.is_hidden():
                continue

            # Don't duplicate default commands
            if not sub_command.config.is_default():
                formats_to_print.append((sub_command.args_format, False))

        app_name = command.application.config.name
        prefix = "    " if len(formats_to_print) > 1 else ""

        layout.add(Paragraph("<b>USAGE</b>"))
        with layout.block():
            for vars in formats_to_print:
                self._render_synopsis(layout, vars[0], app_name, prefix, vars[1])
                prefix = "or: "

            if command.has_aliases():
                layout.add(EmptyLine())
                self._render_aliases(layout, command.aliases)

        layout.add(EmptyLine())

    def _render_aliases(
        self, layout, aliases
    ):  # type: (BlockLayout, Iterable[str]) -> None
        layout.add(Paragraph("aliases: {}".format(", ".join(aliases))))

    def _render_sub_commands(
        self, layout, sub_commands
    ):  # type: (BlockLayout, CommandCollection) -> None
        layout.add(Paragraph("<b>COMMANDS</b>"))

        with layout.block():
            for sub_command in sorted(sub_commands, key=lambda c: c.name):
                self._render_sub_command(layout, sub_command)

    def _render_sub_command(
        self, layout, command
    ):  # type: (BlockLayout, Command) -> None
        config = command.config
        if config.is_hidden():
            return

        description = config.description
        help = config.help
        arguments = command.args_format.get_arguments(False)
        options = command.args_format.get_options(False)

        # TODO: option commands
        name = "<u>{}</u>".format(command.name)

        layout.add(Paragraph(name))

        with layout.block():
            if description:
                self._render_sub_command_description(layout, description)

            if help:
                self._render_sub_command_help(layout, help)

            if arguments:
                self._render_sub_command_arguments(layout, arguments.values())

            if options:
                self._render_sub_command_options(layout, options.values())

            if not description and not help and not arguments and not options:
                layout.add(EmptyLine())

    def _render_sub_command_description(
        self, layout, description
    ):  # type: (BlockLayout, str) -> None
        layout.add(Paragraph(description))
        layout.add(EmptyLine())

    def _render_sub_command_help(
        self, layout, help
    ):  # type: (BlockLayout, str) -> None
        layout.add(Paragraph(help))
        layout.add(EmptyLine())

    def _render_sub_command_arguments(
        self, layout, arguments
    ):  # type: (BlockLayout, Iterable[Argument]) -> None
        for argument in arguments:
            self._render_argument(layout, argument)

        layout.add(EmptyLine())

    def _render_sub_command_options(
        self, layout, options
    ):  # type: (BlockLayout, Iterable[Option]) -> None
        for option in options:
            self._render_option(layout, option)

        layout.add(EmptyLine())

    def _render_description(self, layout, help):  # type: (BlockLayout, str) -> None
        script_name = "console"
        application = self._command.application
        if application and application.config.name:
            script_name = application.config.name

        help = help.format(script_name=script_name, command_name=self._command.name)

        layout.add(Paragraph("<b>DESCRIPTION</b>"))
        with layout.block():
            for paragraph in help.split("\n"):
                layout.add(Paragraph(paragraph))

        layout.add(EmptyLine())
