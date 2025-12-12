import sys

from .api.application import Application as BaseApplication
from .api.args.raw_args import RawArgs
from .api.args.format.args_format import ArgsFormat
from .api.command import Command
from .api.command import CommandCollection
from .api.command.exceptions import CannotAddCommandException
from .api.config.application_config import ApplicationConfig
from .api.config.command_config import CommandConfig
from .api.event import CONFIG
from .api.event import PRE_RESOLVE
from .api.event import ConfigEvent
from .api.event import PreResolveEvent
from .api.exceptions import CliKitException
from .api.io import IO
from .api.io import InputStream
from .api.io import OutputStream
from .api.io.flags import VERY_VERBOSE
from .api.resolver.resolved_command import ResolvedCommand
from .args.argv_args import ArgvArgs
from .io import ConsoleIO
from .ui.components.exception_trace import ExceptionTrace


class ConsoleApplication(BaseApplication):
    """
    A console application
    """

    def __init__(self, config):  # type: (ApplicationConfig) -> None
        self._preliminary_io = ConsoleIO()

        # Enable trace output for exceptions thrown during boot
        self._preliminary_io.set_verbosity(VERY_VERBOSE)

        self._dispatcher = None

        try:
            dispatcher = config.dispatcher
            if dispatcher and dispatcher.has_listeners(CONFIG):
                dispatcher.dispatch(CONFIG, ConfigEvent(config))

            self._config = config
            self._dispatcher = config.dispatcher
            self._commands = CommandCollection()
            self._named_commands = CommandCollection()
            self._default_commands = CommandCollection()
            self._global_args_format = ArgsFormat(
                list(config.arguments.values()) + list(config.options.values())
            )

            for command_config in config.command_configs:
                self.add_command(command_config)
        except Exception as e:
            if not config.is_exception_caught():
                raise

            # Render the trace to the preliminary IO
            trace = ExceptionTrace(e)
            trace.render(self._preliminary_io)

            # Ignore is_terminated_after_run() setting. This is a fatal error.
            sys.exit(self.exception_to_exit_code(e))

    @property
    def config(self):  # type: () -> ApplicationConfig
        return self._config

    @property
    def global_args_format(self):  # type: () -> ArgsFormat
        return self._global_args_format

    def get_command(self, name):  # type: (str) -> Command
        return self._commands.get(name)

    @property
    def commands(self):  # type: () -> CommandCollection
        return self._commands

    def has_command(self, name):  # type: (str) -> bool
        return name in self._commands

    def has_commands(self):  # type: () -> bool
        return not self._commands.is_empty()

    @property
    def named_commands(self):  # type: () -> CommandCollection
        return self._named_commands

    def has_named_commands(self):  # type: () -> bool
        return not self._named_commands.is_empty()

    @property
    def default_commands(self):  # type: () -> CommandCollection
        return self._default_commands

    def has_default_commands(self):  # type: () -> bool
        return not self._default_commands.is_empty()

    def resolve_command(self, args):  # type: (RawArgs) -> ResolvedCommand
        if self._dispatcher and self._dispatcher.has_listeners(PRE_RESOLVE):
            event = PreResolveEvent(args, self)
            self._dispatcher.dispatch(PRE_RESOLVE, event)

            resolved_command = event.resolved_command
            if resolved_command:
                return resolved_command

        return self._config.command_resolver.resolve(args, self)

    def run(
        self, args=None, input_stream=None, output_stream=None, error_stream=None
    ):  # type: (RawArgs, InputStream, OutputStream, OutputStream) -> int
        # Render errors to the preliminary IO until the final IO is created
        io = self._preliminary_io
        try:
            if args is None:
                args = ArgvArgs()

            io_factory = self._config.io_factory

            io = io_factory(
                self, args, input_stream, output_stream, error_stream
            )  # type: IO

            resolved_command = self.resolve_command(args)
            command = resolved_command.command
            parsed_args = resolved_command.args

            status_code = command.handle(parsed_args, io)
        except KeyboardInterrupt:
            status_code = 1
        except Exception as e:
            if not self._config.is_exception_caught():
                raise

            trace = ExceptionTrace(
                e,
                solution_provider_repository=self._config.solution_provider_repository,
            )
            trace.render(io, simple=isinstance(e, CliKitException))

            status_code = self.exception_to_exit_code(e)

        if self._config.is_terminated_after_run():
            sys.exit(status_code)

        return status_code

    def exception_to_exit_code(self, e):  # type: (Exception) -> int
        if not hasattr(e, "code") or not isinstance(e, int):
            return 1

        return min(max(e.code, 1), 255)

    def add_command(self, config):  # type: (CommandConfig) -> None
        if not config.is_enabled():
            return

        self._validate_command_name(config.name)

        command = Command(config, self)
        self._commands.add(command)

        if config.is_default():
            self._default_commands.add(command)

        if not config.is_anonymous():
            self._named_commands.add(command)

    def _validate_command_name(self, name):  # type: (Optional[str]) -> None
        if not name:
            raise CannotAddCommandException.name_empty()

        if name in self._commands:
            raise CannotAddCommandException.name_exists(name)
