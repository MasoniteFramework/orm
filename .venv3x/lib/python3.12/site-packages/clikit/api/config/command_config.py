from contextlib import contextmanager

from typing import Any
from typing import List
from typing import Optional

from clikit.api.args.args_parser import ArgsParser
from clikit.api.args.format.args_format import ArgsFormat
from clikit.api.args.format.args_format_builder import ArgsFormatBuilder
from clikit.api.args.format.command_name import CommandName
from clikit.api.command.exceptions import NoSuchCommandException

from .config import Config


class CommandConfig(Config):
    """
    The configuration of a console command.
    """

    def __init__(self, name=None):  # type: (Optional[str]) -> None
        super(CommandConfig, self).__init__()

        self._name = name
        self._aliases = []
        self._description = ""
        self._help = None
        self._enabled = True
        self._hidden = False
        self._process_title = None
        self._default = None
        self._anonymous = None
        self._sub_command_configs = []  # type: List[CommandConfig]

        self._parent_config = None  # type: Optional[CommandConfig]

    @property
    def name(self):  # type: () -> Optional[str]
        return self._name

    def set_name(self, name):  # type: (Optional[str]) -> CommandConfig
        self._name = name

        return self

    @property
    def aliases(self):  # type: () -> List[str]
        return self._aliases

    def add_alias(self, alias):  # type: (str) -> CommandConfig
        self._aliases.append(alias)

        return self

    def add_aliases(self, aliases):  # type: (List[str]) -> CommandConfig
        for alias in aliases:
            self.add_alias(alias)

        return self

    def set_aliases(self, aliases):  # type: (List[str]) -> CommandConfig
        self._aliases = []

        return self.add_aliases(aliases)

    @property
    def description(self):  # type: () -> str
        return self._description

    def set_description(self, description):  # type: (str) -> CommandConfig
        self._description = description

        return self

    @property
    def help(self):  # type: () -> Optional[str]
        return self._help

    def set_help(self, help):  # type: (Optional[str]) -> CommandConfig
        self._help = help

        return self

    def is_enabled(self):  # type: () -> bool
        return self._enabled

    def enable(self):  # type: () -> CommandConfig
        self._enabled = True

        return self

    def disable(self):  # type: () -> CommandConfig
        self._enabled = False

        return self

    def is_hidden(self):  # type: () -> bool
        return self._hidden

    def hide(self, hidden=True):  # type: (bool) -> CommandConfig
        self._hidden = hidden

        return self

    @property
    def process_title(self):  # type: () -> Optional[str]
        return self._process_title

    def set_process_title(
        self, process_title
    ):  # type: (Optional[str]) -> CommandConfig
        self._process_title = process_title

        return self

    def default(self, default=True):  # type: (bool) -> CommandConfig
        """
        Marks the command as the default command.
        """
        self._default = default
        self._anonymous = False

        return self

    def anonymous(self):  # type: () -> CommandConfig
        self._default = True
        self._anonymous = True

        return self

    def is_default(self):  # type: () -> bool
        return self._default

    def is_anonymous(self):  # type: () -> bool
        return self._anonymous

    @property
    def parent_config(self):  # type: () -> Optional[CommandConfig]
        return self._parent_config

    def set_parent_config(
        self, parent_config
    ):  # type: (Optional[CommandConfig]) -> CommandConfig
        self._parent_config = parent_config

        return self

    def is_sub_command_config(self):  # type: () -> bool
        return self._parent_config is not None

    def build_args_format(
        self, base_format=None
    ):  # type: (Optional[ArgsFormat]) -> ArgsFormat
        builder = ArgsFormatBuilder(base_format)

        if not self._anonymous:
            builder.add_command_name(CommandName(self.name, self.aliases))

        builder.add_options(*self.options.values())
        builder.add_arguments(*self.arguments.values())

        return builder.format

    @contextmanager
    def sub_command(self, name):  # type: (str) -> CommandConfig
        sub_command_config = CommandConfig(name)
        self.add_sub_command_config(sub_command_config)

        yield sub_command_config

    def create_sub_command(self, name):  # type: (str) -> CommandConfig
        sub_command_config = CommandConfig(name)
        self.add_sub_command_config(sub_command_config)

        return sub_command_config

    @contextmanager
    def edit_sub_command(self, name):  # type: (str) -> CommandConfig
        sub_command_config = self.get_sub_command_config(name)

        yield sub_command_config

    def add_sub_command_config(
        self, sub_command_config
    ):  # type: (CommandConfig) -> CommandConfig
        self._sub_command_configs.append(sub_command_config)

        return self

    def add_sub_command_configs(
        self, sub_command_configs
    ):  # type: (List[CommandConfig]) -> CommandConfig
        for sub_command_config in sub_command_configs:
            self.add_sub_command_config(sub_command_config)

        return self

    def get_sub_command_config(self, name):  # type: (str) -> CommandConfig
        for sub_command_config in self._sub_command_configs:
            if sub_command_config.name == name:
                return sub_command_config

        raise NoSuchCommandException(name)

    @property
    def sub_command_configs(self):  # type: () -> List[CommandConfig]
        return self._sub_command_configs

    def has_sub_command_config(self, name):  # type: (str) -> bool
        for sub_command_config in self._sub_command_configs:
            if sub_command_config.name == name:
                return True

        return False

    def has_sub_command_configs(self):  # type: () -> bool
        return len(self._sub_command_configs) > 0

    @property
    def default_helper_set(self):  # type: () -> HelperSet
        if self._parent_config:
            return self._parent_config.default_helper_set

        return super(CommandConfig, self).default_helper_set

    @property
    def default_args_parser(self):  # type: () -> ArgsParser
        if self._parent_config:
            return self._parent_config.default_args_parser

        return super(CommandConfig, self).default_args_parser

    @property
    def default_lenient_args_parsing(self):  # type: () -> bool
        if self._parent_config:
            return self._parent_config.default_lenient_args_parsing

        return super(CommandConfig, self).default_lenient_args_parsing

    @property
    def default_handler(self):  # type: () -> Any
        if self._parent_config:
            return self._parent_config.default_handler

        return super(CommandConfig, self).default_handler

    @property
    def default_handler_method(self):  # type: () -> str
        if self._parent_config:
            return self._parent_config.default_handler_method

        return super(CommandConfig, self).default_handler_method
