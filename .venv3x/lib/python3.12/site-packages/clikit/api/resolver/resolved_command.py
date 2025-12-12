from clikit.api.args import Args
from clikit.api.command import Command


class ResolvedCommand(object):
    """
    A resolved command.
    """

    def __init__(self, command, args):  # type: (Command, Args) -> None
        self._command = command
        self._args = args

    @property
    def command(self):  # type: () -> Command
        return self._command

    @property
    def args(self):  # type: () -> Args
        return self._args
