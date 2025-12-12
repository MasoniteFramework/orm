from typing import Any
from typing import Dict
from typing import Optional

from clikit.api.args.args_parser import ArgsParser
from clikit.api.args.format.args_format_builder import ArgsFormatBuilder
from clikit.api.args.format.argument import Argument
from clikit.api.args.format.option import Option
from clikit.args.default_args_parser import DefaultArgsParser


class Config(object):
    """
    Implements methods shared by all configurations.
    """

    def __init__(self):
        self._format_builder = ArgsFormatBuilder()
        self._helper_set = None
        self._args_parser = None
        self._lenient_args_parsing = None
        self._handler = None
        self._handler_method = None

        self.configure()

    @property
    def arguments(self):  # type: () -> Dict[str, Argument]
        return self._format_builder.get_arguments()

    def add_argument(
        self, name, flags=0, description=None, default=None
    ):  # type: (str, int, Optional[str], Any) -> Config
        argument = Argument(name, flags, description, default)

        self._format_builder.add_argument(argument)

        return self

    @property
    def options(self):  # type: () -> Dict[str, Option]
        return self._format_builder.get_options()

    def add_option(
        self,
        long_name,
        short_name=None,
        flags=0,
        description=None,
        default=None,
        value_name="...",
    ):  # type: (str, Optional[str], int, Optional[str], Any, str) -> Config
        option = Option(long_name, short_name, flags, description, default, value_name)

        self._format_builder.add_option(option)

        return self

    @property
    def helper_set(self):  # type: () -> HelperSet
        if self._helper_set is None:
            return self.default_helper_set

        return self._helper_set

    def set_helper_set(self, helper_set):  # type: (HelperSet) -> Config
        self._helper_set = helper_set

        return self

    @property
    def args_parser(self):  # type: () -> ArgsParser
        if self._args_parser is None:
            return self.default_args_parser

        return self._args_parser

    def set_args_parser(self, args_parser):  # type: (ArgsParser) -> Config
        self._args_parser = args_parser

        return self

    def is_lenient_args_parsing_enabled(self):  # type: () -> bool
        if self._lenient_args_parsing is None:
            return self.default_lenient_args_parsing

        return self._lenient_args_parsing

    def enable_lenient_args_parsing(self):  # type: () -> Config
        self._lenient_args_parsing = True

        return self

    def disable_lenient_args_parsing(self):  # type: () -> Config
        self._lenient_args_parsing = False

        return self

    @property
    def handler(self):  # type: () -> Any
        if self._handler is None:
            return self.default_handler

        if callable(self._handler):
            return self._handler()

        return self._handler

    def set_handler(self, handler):  # type: (Any) -> Config
        self._handler = handler

        return self

    @property
    def handler_method(self):  # type: () -> str
        if self._handler_method is None:
            return self.default_handler_method

        return self._handler_method

    def set_handler_method(self, handler_method):  # type: (str) -> Config
        self._handler_method = handler_method

        return self

    @property
    def default_helper_set(self):  # type: () -> HelperSet
        return HelperSet()

    @property
    def default_args_parser(self):  # type: () -> ArgsParser
        return DefaultArgsParser()

    @property
    def default_lenient_args_parsing(self):  # type: () -> bool
        return False

    @property
    def default_handler(self):  # type: () -> Any
        return lambda: None

    @property
    def default_handler_method(self):  # type: () -> Any
        return "handle"

    def configure(self):  # type: () -> None
        """
        Adds the default configuration.

        Should be overridden in subclasses
        """
