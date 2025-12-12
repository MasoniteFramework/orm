# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from typing import Any
from typing import Iterable

from clikit.api.args.format import Argument
from clikit.api.args.format import ArgsFormat
from clikit.api.args.format import Option
from clikit.api.io import IO

from clikit.ui import Component
from clikit.ui.components import EmptyLine
from clikit.ui.components import LabeledParagraph
from clikit.ui.components import Paragraph
from clikit.ui.layout import BlockLayout


class AbstractHelp(Component):
    """
    Base class for rendering help pages.
    """

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        layout = BlockLayout()

        self._render_help(layout)

        layout.render(io, indentation)

    def _render_help(self, layout):  # type: (BlockLayout) -> None
        raise NotImplementedError()

    def _render_arguments(
        self, layout, arguments
    ):  # type: (BlockLayout, Iterable[Argument]) -> None
        layout.add(Paragraph("<b>ARGUMENTS</b>"))

        with layout.block():
            for argument in arguments:
                self._render_argument(layout, argument)

        layout.add(EmptyLine())

    def _render_argument(
        self, layout, argument
    ):  # type: (BlockLayout, Argument) -> None
        description = argument.description
        name = "<c1><{}></c1>".format(argument.name)
        default = argument.default

        if default is not None and (not isinstance(default, list) or len(default) > 0):
            description += " <b>{}</b>".format(self._format_value(default))

        layout.add(LabeledParagraph(name, description))

    def _render_options(
        self, layout, options
    ):  # type: (BlockLayout, Iterable[Option]) -> None
        layout.add(Paragraph("<b>OPTIONS</b>"))

        with layout.block():
            for option in options:
                self._render_option(layout, option)

        layout.add(EmptyLine())

    def _render_global_options(
        self, layout, options
    ):  # type: (BlockLayout, Iterable[Option]) -> None
        layout.add(Paragraph("<b>GLOBAL OPTIONS</b>"))

        with layout.block():
            for option in options:
                self._render_option(layout, option)

        layout.add(EmptyLine())

    def _render_option(self, layout, option):  # type: (BlockLayout, Option) -> None
        description = option.description
        default = option.default

        alternative_name = None
        if option.is_long_name_preferred():
            preferred_name = "--{}".format(option.long_name)
            if option.short_name:
                alternative_name = "-{}".format(option.short_name)
        else:
            preferred_name = "-{}".format(option.short_name)
            alternative_name = "--{}".format(option.long_name)

        name = "<c1>{}</c1>".format(preferred_name)
        if alternative_name:
            name += " ({})".format(alternative_name)

        if (
            option.accepts_value()
            and default is not None
            and (not isinstance(default, list) or len(default) > 0)
        ):
            description += " <b>(default: {})</b>".format(self._format_value(default))

        if option.is_multi_valued():
            description += " <b>(multiple values allowed)</b>"

        layout.add(LabeledParagraph(name, description))

    def _render_synopsis(
        self, layout, args_format, app_name, prefix="", last_optional=False
    ):  # type: (BlockLayout, ArgsFormat, str, str, bool) -> None
        name_parts = []
        argument_parts = []

        name_parts.append("<u>{}</u>".format(app_name or "console"))

        for command_name in args_format.get_command_names():
            name_parts.append("<u>{}</u>".format(command_name.string))

        for command_option in args_format.get_command_options():
            if command_option.is_long_name_preferred():
                name_parts.append("--{}".format(command_option.long_name))
            else:
                name_parts.append("-{}".format(command_option.short_name))

        if last_optional:
            name_parts[-1] = "[{}]".format(name_parts[-1])

        for option in args_format.get_options(False).values():
            # \xC2\xA0 is a non-breaking space
            if option.is_value_required():
                fmt = "{}\u00A0<{}>"
            elif option.is_value_optional():
                fmt = "{}\u00A0[<{}>]"
            else:
                fmt = "{}"

            if option.is_long_name_preferred():
                option_name = "--{}".format(option.long_name)
            else:
                option_name = "-{}".format(option.short_name)

            argument_parts.append(
                "[{}]".format(fmt.format(option_name, option.value_name))
            )

        for argument in args_format.get_arguments().values():
            arg_name = argument.name

            argument_parts.append(
                ("<{}>" if argument.is_required() else "[<{}>]").format(
                    arg_name + str(int(argument.is_multi_valued()) or "")
                )
            )

            if argument.is_multi_valued():
                argument_parts.append("... [<{}N>]".format(arg_name))

        args_opts = " ".join(argument_parts)
        name = " ".join(name_parts)

        layout.add(LabeledParagraph(prefix + name, args_opts, 1, False))

    def _format_value(self, value):  # type: (Any) -> str
        return json.dumps(value)
