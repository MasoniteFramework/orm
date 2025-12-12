from typing import List
from typing import Optional

from clikit.api.args.args import Args
from clikit.api.args.raw_args import RawArgs
from clikit.api.args.format.args_format import ArgsFormat
from clikit.api.config.command_config import CommandConfig
from clikit.api.event import PRE_HANDLE
from clikit.api.event import PreHandleEvent
from clikit.api.io import IO


class Command(object):
    """
    A console command.
    """

    def __init__(
        self, config, application=None, parent_command=None
    ):  # type: (CommandConfig, Optional[Application], Optional[Command]) -> None
        from .command_collection import CommandCollection

        if not config.name:
            raise RuntimeError("The name of the command config must be set.")

        self._name = config.name
        self._short_name = None
        self._aliases = config.aliases
        self._config = config
        self._application = application
        self._parent_command = parent_command
        self._sub_commands = CommandCollection()
        self._named_sub_commands = CommandCollection()
        self._default_sub_commands = CommandCollection()
        self._args_format = config.build_args_format(self.base_format)
        self._dispatcher = application.config.dispatcher if application else None

        for sub_config in config.sub_command_configs:
            self.add_sub_command(sub_config)

    @property
    def name(self):  # type: () -> str
        return self._name

    @property
    def short_name(self):  # type: () -> str
        return self._short_name

    @property
    def full_name(self):  # type: () -> str
        if self._parent_command:
            return "{} {}".format(str(self._parent_command.full_name), self._name)

        return self._name

    @property
    def aliases(self):  # type: () -> List[str]
        return self._aliases

    def has_aliases(self):  # type: () -> bool
        return len(self._aliases) > 0

    @property
    def config(self):  # type: () -> CommandConfig
        return self._config

    @property
    def args_format(self):  # type: () -> ArgsFormat
        return self._args_format

    @property
    def application(self):  # type: () -> Application
        return self._application

    @property
    def parent_command(self):  # type: () -> Command
        return self._parent_command

    @property
    def sub_commands(self):  # type: () -> CommandCollection
        return self._sub_commands

    def get_sub_command(self, name):  # type: (str) -> Command
        return self._sub_commands.get(name)

    def has_sub_commands(self):  # type: () -> bool
        return len(self._sub_commands) > 0

    @property
    def named_sub_commands(self):  # type: () -> CommandCollection
        return self._named_sub_commands

    def get_named_sub_command(self, name):  # type: (str) -> Command
        return self._named_sub_commands.get(name)

    def has_named_sub_commands(self):  # type: () -> bool
        return len(self._named_sub_commands) > 0

    @property
    def default_sub_commands(self):  # type: () -> CommandCollection
        return self._default_sub_commands

    def get_default_sub_command(self, name):  # type: (str) -> Command
        return self._default_sub_commands.get(name)

    def has_default_sub_commands(self):  # type: () -> bool
        return len(self._default_sub_commands) > 0

    def parse(self, args, lenient=None):  # type: (RawArgs, Optional[bool]) -> Args
        if lenient is None:
            lenient = self._config.is_lenient_args_parsing_enabled()

        return self._config.args_parser.parse(args, self._args_format, lenient)

    def run(self, args, io):  # type: (RawArgs, IO) -> int
        return self.handle(self.parse(args), io)

    def handle(self, args, io):  # type: (Args, IO) -> int
        try:
            status_code = self._do_handle(args, io)
        except KeyboardInterrupt:
            if io.is_debug():
                raise

            status_code = 1

        # Any empty value is considered a success
        if not status_code:
            return 0

        # Anything else is normalized to a valid error status code
        return min(max(int(status_code), 1), 255)

    @property
    def base_format(self):  # type: () -> Optional[ArgsFormat]
        if self._parent_command:
            return self._parent_command.args_format

        if self._application:
            return self._application.global_args_format

        return

    def add_sub_command(self, config):  # type: (CommandConfig) -> None
        if not config.is_enabled():
            return

        command = self.__class__(config, self._application, self)

        # TODO: Validate command

        self._sub_commands.add(command)

        if config.is_default():
            self._default_sub_commands.add(command)

        if not config.is_anonymous():
            self._named_sub_commands.add(command)

    def _do_handle(self, args, io):  # type: (Args, IO) -> Optional[int]
        if self._dispatcher and self._dispatcher.has_listeners(PRE_HANDLE):
            event = PreHandleEvent(args, io, self)
            self._dispatcher.dispatch(PRE_HANDLE, event)

            if event.is_handled():
                return event.status_code

        handler = self._config.handler
        handler_method = self._config.handler_method

        return getattr(handler, handler_method)(args, io, self)

    def __repr__(self):  # type: () -> str
        return "<Command {}>".format(self.full_name)
