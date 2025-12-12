from clikit.api.args import RawArgs
from clikit.api.resolver import ResolvedCommand

from .event import Event


class PreResolveEvent(Event):
    """
    Dispatched before the console arguments are resolved to a command.

    Add a listener for this event to customize the command used for the given
    console arguments.
    """

    def __init__(self, raw_args, application):  # type: (RawArgs, Application) -> None
        super(PreResolveEvent, self).__init__()

        self._raw_args = raw_args
        self._application = application
        self._resolved_command = None

    @property
    def raw_args(self):  # type: () -> RawArgs
        return self._raw_args

    @property
    def application(self):  # type: () -> Application
        return self._application

    @property
    def resolved_command(self):  # type: () -> ResolvedCommand
        return self._resolved_command

    def set_resolved_command(
        self, resolved_command=None
    ):  # type: (ResolvedCommand) -> None
        self._resolved_command = resolved_command
