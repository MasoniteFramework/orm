from clikit.api.args import Args
from clikit.api.io import IO

from .event import Event


class PreHandleEvent(Event):
    """
    Dispatched before a command is handled.

    Add a listener for this event to execute custom logic before or instead of
    the default handler.
    """

    def __init__(self, args, io, command):  # type: (Args, IO, Command) -> None
        super(PreHandleEvent, self).__init__()

        self._args = args
        self._io = io
        self._command = command
        self._handled = False
        self._status_code = 0

    @property
    def args(self):  # type: () -> Args
        return self._args

    @property
    def io(self):  # type: () -> IO
        return self._io

    @property
    def command(self):  # type: () -> Command
        return self._command

    @property
    def status_code(self):  # type: () -> int
        return self._status_code

    def is_handled(self):  # type: () -> bool
        return self._handled

    def handled(self, handled):  # type: (bool) -> None
        self._handled = handled

    def set_status_code(self, status_code):  # type: (int) -> None
        self._status_code = status_code
