from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from clikit.utils._compat import OrderedDict

from ..exceptions import CannotAddArgumentException
from ..exceptions import CannotAddOptionException
from ..exceptions import NoSuchArgumentException
from ..exceptions import NoSuchOptionException
from .args_format import ArgsFormat
from .argument import Argument
from .option import Option
from .command_name import CommandName
from .command_option import CommandOption


class ArgsFormatBuilder(object):
    """
    A builder for ArgsFormat instances.
    """

    def __init__(self, base_format=None):  # type: (Optional[ArgsFormat]) -> None
        self._base_format = base_format
        self._command_names = []
        self._command_options = OrderedDict()
        self._command_options_by_short_name = OrderedDict()
        self._arguments = OrderedDict()
        self._options = OrderedDict()
        self._options_by_short_name = OrderedDict()
        self._has_multi_valued_arg = False
        self._hash_optional_arg = False

    @property
    def base_format(self):  # type: () -> Optional[ArgsFormat]
        return self._base_format

    def set_command_names(
        self, *command_names
    ):  # type: (Tuple[CommandName]) -> ArgsFormatBuilder
        self._command_names = []

        self.add_command_names(*command_names)

        return self

    def add_command_names(
        self, *command_names
    ):  # type: (Tuple[CommandName]) -> ArgsFormatBuilder
        for command_name in command_names:
            self.add_command_name(command_name)

        return self

    def add_command_name(
        self, command_name
    ):  # type: (CommandName) -> ArgsFormatBuilder
        self._command_names.append(command_name)

        return self

    def has_command_names(self, include_base=True):  # type: (bool) -> bool
        if self._command_names:
            return True

        if include_base and self._base_format:
            return self._base_format.has_command_names()

        return False

    def get_command_names(self, include_base=True):  # type: (bool) -> List[CommandName]
        command_names = self._command_names

        if include_base and self._base_format:
            command_names = self._base_format.get_command_names() + command_names

        return command_names

    def set_command_options(
        self, *command_options
    ):  # type: (Tuple[CommandOption]) -> ArgsFormatBuilder
        self._command_options = {}
        self._command_options_by_short_name = {}

        self.add_command_options(*command_options)

    def add_command_options(
        self, *command_options
    ):  # type: (Tuple[CommandOption]) -> ArgsFormatBuilder
        for command_option in command_options:
            self.add_command_option(command_option)

    def add_command_option(
        self, command_option
    ):  # type: (CommandOption) -> ArgsFormatBuilder
        long_name = command_option.long_name
        short_name = command_option.short_name
        long_aliases = command_option.long_aliases
        short_aliases = command_option.short_aliases

        if self.has_option(long_name) or self.has_command_option(long_name):
            raise CannotAddOptionException.already_exists(long_name)

        for long_alias in long_aliases:
            if self.has_option(long_alias) or self.has_command_option(long_alias):
                raise CannotAddOptionException.already_exists(long_alias)

        if self.has_option(short_name) or self.has_command_option(short_name):
            raise CannotAddOptionException.already_exists(short_name)

        for short_alias in short_aliases:
            if self.has_option(short_alias) or self.has_command_option(short_alias):
                raise CannotAddOptionException.already_exists(short_alias)

        self._command_options[long_name] = command_option

        if short_name:
            self._command_options_by_short_name[short_name] = command_option

        for long_alias in long_aliases:
            self._command_options[long_alias] = command_option

        for short_alias in short_aliases:
            self._command_options_by_short_name[short_alias] = command_option

        return self

    def has_command_option(self, name, include_base=True):  # type: (str, bool) -> bool
        if name in self._command_options or name in self._command_options_by_short_name:
            return True

        if include_base and self._base_format:
            return self._base_format.has_command_option(name)

        return False

    def has_command_options(self, include_base=True):  # type: (bool) -> bool
        if self._command_options:
            return True

        if include_base and self._base_format:
            return self._base_format.has_command_options()

        return False

    def get_command_option(
        self, name, include_base=True
    ):  # type: (str, bool) -> CommandOption
        if name in self._command_options:
            return self._command_options[name]

        if name in self._command_options_by_short_name:
            return self._command_options_by_short_name[name]

        if include_base and self._base_format:
            return self._base_format.get_command_option(name)

        raise NoSuchOptionException(name)

    def get_command_options(
        self, include_base=True
    ):  # type: (bool) -> Iterable[CommandOption]
        command_options = list(self._command_options.values())

        if include_base and self._base_format:
            command_options += self._base_format.get_command_options()

        return command_options

    def set_arguments(
        self, *arguments
    ):  # type: (Iterable[Argument]) -> ArgsFormatBuilder
        self._arguments = {}
        self._has_multi_valued_arg = False
        self._hash_optional_arg = False

        self.add_arguments(*arguments)

        return self

    def add_arguments(
        self, *arguments
    ):  # type: (Iterable[Argument]) -> ArgsFormatBuilder
        for argument in arguments:
            self.add_argument(argument)

        return self

    def add_argument(self, argument):  # type: (Argument) -> ArgsFormatBuilder
        name = argument.name

        if self.has_argument(name):
            raise CannotAddArgumentException.already_exists(name)

        if self.has_multi_valued_argument():
            raise CannotAddArgumentException.cannot_add_after_multi_valued()

        if argument.is_required() and self.has_optional_argument():
            raise CannotAddArgumentException.cannot_add_required_after_optional()

        if argument.is_multi_valued():
            self._has_multi_valued_arg = True

        if argument.is_optional():
            self._hash_optional_arg = True

        self._arguments[name] = argument

        return self

    def has_argument(
        self, name, include_base=True
    ):  # type: (Union[str, int], bool) -> bool
        arguments = self.get_arguments(include_base)

        if isinstance(name, int):
            return name < len(arguments)

        return name in arguments

    def has_multi_valued_argument(self, include_base=True):  # type: (bool) -> bool
        if self._has_multi_valued_arg:
            return True

        if include_base and self._base_format:
            return self._base_format.has_multi_valued_argument()

        return False

    def has_optional_argument(self, include_base=True):  # type: (bool) -> bool
        if self._hash_optional_arg:
            return True

        if include_base and self._base_format:
            return self._base_format.has_optional_argument()

        return False

    def has_required_argument(self, include_base=True):  # type: (bool) -> bool
        if not self._hash_optional_arg and self._arguments:
            return True

        if include_base and self._base_format:
            return self._base_format.has_required_argument()

        return False

    def has_arguments(self, include_base=True):  # type: (bool) -> bool
        if self._arguments:
            return True

        if include_base and self._base_format:
            return self._base_format.has_arguments()

        return False

    def get_argument(
        self, name, include_base=True
    ):  # type: (Union[str, int], bool) -> Argument
        if isinstance(name, int):
            arguments = list(self.get_arguments(include_base).values())

            if name >= len(arguments):
                raise NoSuchArgumentException(name)
        else:
            arguments = self.get_arguments(include_base)

            if name not in arguments:
                raise NoSuchArgumentException(name)

        return arguments[name]

    def get_arguments(self, include_base=True):  # type: (bool) -> Dict[str, Argument]
        arguments = self._arguments.copy()

        if include_base and self._base_format:
            arguments.update(self._base_format.get_arguments())

        return arguments

    def set_options(self, *options):  # type: (Iterable[Option]) -> ArgsFormatBuilder
        self._options = {}
        self._options_by_short_name = {}

        self.add_options(*options)

    def add_options(self, *options):  # type: (Iterable[Option]) -> ArgsFormatBuilder
        for option in options:
            self.add_option(option)

    def add_option(self, option):  # type: (Option) -> ArgsFormatBuilder
        long_name = option.long_name
        short_name = option.short_name

        if self.has_option(long_name) or self.has_command_option(long_name):
            raise CannotAddOptionException.already_exists(long_name)

        if self.has_option(short_name) or self.has_command_option(short_name):
            raise CannotAddOptionException.already_exists(short_name)

        self._options[long_name] = option

        if short_name:
            self._options_by_short_name[short_name] = option

        return self

    def has_option(self, name, include_base=True):  # type: (str, bool) -> bool
        if name in self._options or name in self._options_by_short_name:
            return True

        if include_base and self._base_format:
            return self._base_format.has_option(name)

        return False

    def has_options(self, include_base=True):  # type: (bool) -> bool
        if self._options:
            return True

        if include_base and self._base_format:
            return self._base_format.has_options()

        return False

    def get_option(self, name, include_base=True):  # type: (str, bool) -> Option
        if name in self._options:
            return self._options[name]

        if name in self._options_by_short_name:
            return self._options_by_short_name[name]

        if include_base and self._base_format:
            return self._base_format.get_option(name)

        raise NoSuchOptionException(name)

    def get_options(self, include_base=True):  # type: (bool) -> Dict[str, Option]
        options = self._options.copy()

        if include_base and self._base_format:
            options.update(self._base_format.get_options())

        return options

    @property
    def format(self):  # type: () -> ArgsFormat
        return ArgsFormat(self, self._base_format)
