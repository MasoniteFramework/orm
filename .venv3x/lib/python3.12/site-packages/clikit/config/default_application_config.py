from clikit.api.config.application_config import ApplicationConfig
from clikit.api.args.raw_args import RawArgs
from clikit.api.args.format.argument import Argument
from clikit.api.args.format.option import Option
from clikit.api.event import PRE_HANDLE
from clikit.api.event import PRE_RESOLVE
from clikit.api.event import EventDispatcher
from clikit.api.event import PreHandleEvent
from clikit.api.event import PreResolveEvent
from clikit.api.io import IO
from clikit.api.io import Input
from clikit.api.io import InputStream
from clikit.api.io import Output
from clikit.api.io import OutputStream
from clikit.api.io.flags import DEBUG
from clikit.api.io.flags import VERBOSE
from clikit.api.io.flags import VERY_VERBOSE
from clikit.api.resolver import ResolvedCommand
from clikit.formatter import AnsiFormatter
from clikit.formatter import DefaultStyleSet
from clikit.formatter import PlainFormatter
from clikit.handler.help import HelpTextHandler
from clikit.io import ConsoleIO
from clikit.io.input_stream import StandardInputStream
from clikit.io.output_stream import ErrorOutputStream
from clikit.io.output_stream import StandardOutputStream
from clikit.resolver.default_resolver import DefaultResolver
from clikit.resolver.help_resolver import HelpResolver
from clikit.ui.components import NameVersion


class DefaultApplicationConfig(ApplicationConfig):
    """
    The default application configuration.
    """

    def configure(self):
        self.set_io_factory(self.create_io)
        self.add_event_listener(PRE_RESOLVE, self.resolve_help_command)
        self.add_event_listener(PRE_HANDLE, self.print_version)

        self.add_option("help", "h", Option.NO_VALUE, "Display this help message")
        self.add_option("quiet", "q", Option.NO_VALUE, "Do not output any message")
        self.add_option(
            "verbose",
            "v",
            Option.OPTIONAL_VALUE,
            "Increase the verbosity of messages: "
            '"-v" for normal output, '
            '"-vv" for more verbose output '
            'and "-vvv" for debug',
        )
        self.add_option(
            "version", "V", Option.NO_VALUE, "Display this application version"
        )
        self.add_option("ansi", None, Option.NO_VALUE, "Force ANSI output")
        self.add_option("no-ansi", None, Option.NO_VALUE, "Disable ANSI output")
        self.add_option(
            "no-interaction",
            "n",
            Option.NO_VALUE,
            "Do not ask any interactive question",
        )

        with self.command("help") as c:
            c.default()
            c.set_description("Display the manual of a command")
            c.add_argument(
                "command", Argument.OPTIONAL | Argument.MULTI_VALUED, "The command name"
            )
            c.set_handler(HelpTextHandler(HelpResolver()))

    def create_io(
        self,
        application,
        args,
        input_stream=None,
        output_stream=None,
        error_stream=None,
    ):  # type: (Application, RawArgs, InputStream, OutputStream, OutputStream) -> IO
        if input_stream is None:
            input_stream = StandardInputStream()

        if output_stream is None:
            output_stream = StandardOutputStream()

        if error_stream is None:
            error_stream = ErrorOutputStream()

        style_set = application.config.style_set

        if args.has_option_token("--no-ansi"):
            output_formatter = error_formatter = PlainFormatter(style_set)
        elif args.has_option_token("--ansi"):
            output_formatter = error_formatter = AnsiFormatter(style_set, True)
        else:
            if output_stream.supports_ansi():
                output_formatter = AnsiFormatter(style_set)
            else:
                output_formatter = PlainFormatter(style_set)

            if error_stream.supports_ansi():
                error_formatter = AnsiFormatter(style_set)
            else:
                error_formatter = PlainFormatter(style_set)

        io = self.io_class(
            Input(input_stream),
            Output(output_stream, output_formatter),
            Output(error_stream, error_formatter),
        )

        if args.has_option_token("-vvv") or self.is_debug():
            io.set_verbosity(DEBUG)
        elif args.has_option_token("-vv"):
            io.set_verbosity(VERY_VERBOSE)
        elif args.has_option_token("-v"):
            io.set_verbosity(VERBOSE)

        if args.has_option_token("--quiet") or args.has_option_token("-q"):
            io.set_quiet(True)

        if args.has_option_token("--no-interaction") or args.has_option_token("-n"):
            io.set_interactive(False)

        return io

    @property
    def io_class(self):  # type: () -> IO.__class__
        return ConsoleIO

    @property
    def default_style_set(self):  # type: () -> DefaultStyleSet
        return DefaultStyleSet()

    @property
    def default_command_resolver(self):  # type: () -> DefaultResolver
        return DefaultResolver()

    def resolve_help_command(
        self, event, event_name, dispatcher
    ):  # type: (PreResolveEvent, str, EventDispatcher) -> None
        args = event.raw_args
        application = event.application

        if args.has_option_token("-h") or args.has_option_token("--help"):
            command = application.get_command("help")

            # Enable lenient parsing
            parsed_args = command.parse(args, True)

            event.set_resolved_command(ResolvedCommand(command, parsed_args))
            event.stop_propagation()

    def print_version(
        self, event, event_name, dispatcher
    ):  # type: (PreHandleEvent, str, EventDispatcher) -> None
        if event.args.is_option_set("version"):
            version = NameVersion(event.command.application.config)
            version.render(event.io)

            event.handled(True)
