from typing import Dict
from typing import List
from typing import Optional


from clikit.api.args.args import Args
from clikit.api.args.args_parser import ArgsParser
from clikit.api.args.format import ArgsFormat
from clikit.api.args.format import Argument
from clikit.api.args.format import CommandName
from clikit.api.args.exceptions import CannotParseArgsException
from clikit.api.args.exceptions import NoSuchOptionException
from clikit.api.args.raw_args import RawArgs

from clikit.utils._compat import OrderedDict


class DefaultArgsParser(ArgsParser):
    """
    Default parser for RawArgs instances.
    """

    def __init__(self):  # type: () -> None
        self._arguments = OrderedDict()
        self._options = OrderedDict()

    def parse(
        self, args, fmt, lenient=False
    ):  # type: (RawArgs, ArgsFormat, bool) -> Args
        self._arguments = OrderedDict()

        arguments = OrderedDict()
        command_names = OrderedDict()
        i = 1
        for j, command_name in enumerate(fmt.get_command_names()):
            arg_name = "cmd{}{}".format(j + 1, i)
            while fmt.has_argument(arg_name):
                i += 1
                arg_name = "cmd{}{}".format(j + 1, i)

            arguments[arg_name] = Argument(arg_name, Argument.REQUIRED)
            command_names[arg_name] = command_name

        arguments.update(fmt.get_arguments())

        _fmt = ArgsFormat(
            fmt.get_command_names()
            + list(arguments.values())
            + list(fmt.get_options().values())
        )

        try:
            self._parse(args, _fmt, lenient)
        except (CannotParseArgsException, NoSuchOptionException):
            if not lenient:
                raise

        self._insert_missing_command_names(arguments, command_names, lenient)

        # Validate
        missing_arguments = [
            arg.name
            for arg in _fmt.get_arguments().values()
            if arg.name not in self._arguments and arg.is_required()
        ]
        if missing_arguments and not lenient:
            raise CannotParseArgsException(
                'Not enough arguments (missing: "{}").'.format(
                    ", ".join(missing_arguments)
                )
            )

        parsed_args = Args(fmt, args)
        for name, value in self._arguments.items():
            if fmt.has_argument(name):
                parsed_args.set_argument(name, value)

        for name, value in self._options.items():
            if fmt.has_option(name):
                parsed_args.set_option(name, value)

        return parsed_args

    def _parse(
        self, raw_args, fmt, lenient
    ):  # type: (RawArgs, ArgsFormat, bool) -> None
        tokens = raw_args.tokens[:]

        parse_options = True
        while True:
            try:
                token = tokens.pop(0)
            except IndexError:
                break

            if parse_options and token == "":
                self._parse_argument(token, fmt, lenient)
            elif parse_options and token == "--":
                parse_options = False
            elif parse_options and token.find("--") == 0:
                self._parse_long_option(token, tokens, fmt, lenient)
            elif parse_options and token[0] == "-" and token != "-":
                self._parse_short_option(token, tokens, fmt, lenient)
            else:
                self._parse_argument(token, fmt, lenient)

    def _insert_missing_command_names(
        self, arguments, command_names, lenient=False
    ):  # type: (Dict[str, Argument], Dict[str, CommandName], bool) -> None
        fixed_values = {}

        actual_values = self._flatten(self._arguments.values())

        command_names_iterator = iter(command_names.values())
        actual_values_iterator = iter(actual_values)
        arguments_iterator = iter(arguments.values())

        actual_value, command_name = self._skip_command_names(
            actual_values_iterator, command_names_iterator, arguments_iterator
        )

        _, argument = self._copy_argument_values(
            command_names_iterator,
            command_name,
            arguments_iterator,
            None,
            fixed_values,
            lenient,
        )
        self._copy_argument_values(
            actual_values_iterator,
            actual_value,
            arguments_iterator,
            argument,
            fixed_values,
            lenient,
        )

        for name, value in fixed_values.items():
            self._arguments[name] = value

    def _skip_command_names(self, actual_values, command_names, arguments):
        arg = next(actual_values, None)
        command_name = next(command_names, None)

        while arg and command_name and command_name.match(arg):
            arg = next(actual_values, None)
            command_name = next(command_names, None)
            next(arguments, None)

        return arg, command_name

    def _copy_argument_values(
        self, actual_values, value, arguments, argument, fixed_values, lenient
    ):
        if value is None:
            value = next(actual_values, None)

        if argument is None:
            argument = next(arguments, None)

        while value is not None:
            if argument is None:
                if lenient:
                    return

                raise CannotParseArgsException.too_many_arguments()

            name = argument.name

            # Append the value to multi-valued arguments
            if argument.is_multi_valued():
                if name not in fixed_values:
                    fixed_values[name] = []

                fixed_values[name].append(value)

                # The multi-valued argument is the last one, so we don't
                # need to advance the array pointer anymore.
            else:
                fixed_values[name] = value

                argument = next(arguments, None)

            value = next(actual_values, None)

        return value, argument

    def _flatten(self, arguments, result=None):
        if result is None:
            result = []

        for value in arguments:
            if isinstance(value, list):
                self._flatten(value, result)
            else:
                result.append(value)

        return result

    def _parse_argument(
        self, token, fmt, lenient
    ):  # type: (str, ArgsFormat, bool) -> None
        c = len(self._arguments)

        # if input is expecting another argument, add it
        if fmt.has_argument(c):
            arg = fmt.get_argument(c)
            if arg.is_multi_valued():
                if arg.name not in self._arguments:
                    self._arguments[arg.name] = []

                self._arguments[arg.name].append(token)
            else:
                self._arguments[arg.name] = token
        elif fmt.has_argument(c - 1) and fmt.get_argument(c - 1).is_multi_valued():
            arg = fmt.get_argument(c - 1)
            if arg.name not in self._arguments:
                self._arguments[arg.name] = []

            self._arguments[arg.name].append(token)
        # unexpected argument
        else:
            if not lenient:
                raise CannotParseArgsException.too_many_arguments()

    def _parse_long_option(
        self, token, tokens, fmt, lenient
    ):  # type: (str, List[str], ArgsFormat, bool) -> None
        name = token[2:]
        pos = name.find("=")
        if pos != -1:
            self._add_long_option(name[:pos], name[pos + 1 :], tokens, fmt, lenient)
        else:
            if fmt.has_option(name) and fmt.get_option(name).accepts_value():
                try:
                    value = tokens.pop(0)
                except IndexError:
                    value = None

                if value and value.startswith("-"):
                    tokens.insert(0, value)
                    value = None

                self._add_long_option(name, value, tokens, fmt, lenient)
            else:
                self._add_long_option(name, None, tokens, fmt, lenient)

    def _parse_short_option(
        self, token, tokens, fmt, lenient
    ):  # type: (str, List[str], ArgsFormat, bool) -> None
        name = token[1:]
        if len(name) > 1:
            if fmt.has_option(name[0]) and fmt.get_option(name[0]).accepts_value():
                # an option with a value (with no space)
                self._add_short_option(name[0], name[1:], tokens, fmt, lenient)
            else:
                self._parse_short_option_set(name, tokens, fmt, lenient)
        else:
            if fmt.has_option(name[0]) and fmt.get_option(name[0]).accepts_value():
                try:
                    value = tokens.pop(0)
                except IndexError:
                    value = None

                if value and value.startswith("-"):
                    tokens.insert(0, value)
                    value = None

                self._add_short_option(name, value, tokens, fmt, lenient)
            else:
                self._add_short_option(name, None, tokens, fmt, lenient)

    def _parse_short_option_set(
        self, name, tokens, fmt, lenient
    ):  # type: (str, List[str], ArgsFormat, bool) -> None
        l = len(name)
        for i in range(0, l):
            if not fmt.has_option(name[i]):
                raise NoSuchOptionException(name[i])

            option = fmt.get_option(name[i])
            if option.accepts_value():
                self._add_long_option(
                    option.long_name,
                    None if l - 1 == i else name[i + 1 :],
                    tokens,
                    fmt,
                    lenient,
                )

                break
            else:
                self._add_long_option(option.long_name, None, tokens, fmt, lenient)

    def _add_long_option(
        self, name, value, tokens, fmt, lenient
    ):  # type: (str, Optional[str], List[str], ArgsFormat, bool) -> None
        if not fmt.has_option(name):
            raise NoSuchOptionException(name)

        option = fmt.get_option(name)

        if value is False:
            value = None

        if value is not None and not option.accepts_value():
            raise CannotParseArgsException.option_does_not_accept_value(name)

        if value is None and option.accepts_value() and len(tokens):
            # if option accepts an optional or mandatory argument
            # let's see if there is one provided
            try:
                nxt = tokens.pop(0)
            except IndexError:
                nxt = None

            if nxt and len(nxt) >= 1 and nxt[0] != "-":
                value = nxt
            elif not nxt:
                value = ""
            else:
                tokens.insert(0, nxt)

        # This test is here to handle cases like --foo=
        # and foo option value is optional
        if value == "":
            value = None

        if value is None:
            if option.is_value_required():
                raise CannotParseArgsException.option_requires_value(name)

            if not option.is_multi_valued():
                value = option.default if option.is_value_optional() else True

        if option.is_multi_valued():
            if name not in self._options:
                self._options[name] = []

            self._options[name].append(value)
        else:
            self._options[name] = value

    def _add_short_option(
        self, name, value, tokens, fmt, lenient
    ):  # type: (str, Optional[str], List[str], ArgsFormat, bool) -> None
        if not fmt.has_option(name):
            raise NoSuchOptionException(name)

        self._add_long_option(
            fmt.get_option(name).long_name, value, tokens, fmt, lenient
        )
