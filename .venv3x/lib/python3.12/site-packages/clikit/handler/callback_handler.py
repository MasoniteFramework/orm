from typing import Callable

from clikit.api.args import Args
from clikit.api.io import IO


class CallbackHandler:
    """
    Delegates command handling to a callable.
    """

    def __init__(self, callback):  # type: (Callable) -> None
        self._calllback = callback

    def handle(self, args, io, _):  # type: (Args, IO, ...) -> int
        return self._calllback(args, io)
