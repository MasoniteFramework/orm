from clikit.api.args.format.args_format import ArgsFormat
from clikit.api.args.raw_args import RawArgs
from clikit.api.command.command_collection import CommandCollection
from clikit.api.config.application_config import ApplicationConfig
from clikit.api.io import InputStream
from clikit.api.io import OutputStream
from clikit.api.resolver.resolved_command import ResolvedCommand


class Application:
    """
    A console application.
    """

    @property
    def config(self):  # type: () -> ApplicationConfig
        raise NotImplementedError()

    @property
    def global_args_format(self):  # type: () -> ArgsFormat
        raise NotImplementedError()

    def get_command(self, name):  # type: (str) -> Command
        raise NotImplementedError()

    @property
    def commands(self):  # type: () -> CommandCollection
        raise NotImplementedError()

    def has_command(self, name):  # type: (str) -> bool
        raise NotImplementedError()

    def has_commands(self):  # type: () -> bool
        raise NotImplementedError()

    @property
    def named_commands(self):  # type: () -> CommandCollection
        raise NotImplementedError()

    def has_named_commands(self):  # type: () -> bool
        raise NotImplementedError()

    @property
    def default_commands(self):  # type: () -> CommandCollection
        raise NotImplementedError()

    def has_default_commands(self):  # type: () -> bool
        raise NotImplementedError()

    def resolve_command(self, args):  # type: (RawArgs) -> ResolvedCommand
        raise NotImplementedError()

    def run(
        self, args=None, input_stream=None, output_stream=None, error_stream=None
    ):  # type: (RawArgs, InputStream, OutputStream, OutputStream) -> int
        raise NotImplementedError()
