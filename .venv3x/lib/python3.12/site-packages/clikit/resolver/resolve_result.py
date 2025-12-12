from clikit.api.args import Args
from clikit.api.args import RawArgs
from clikit.api.args.exceptions import CannotParseArgsException
from clikit.api.command import Command


class ResolveResult(object):
    """
    An intermediate result created during resolving.
    """

    def __init__(self, command, raw_args):  # type: (Command, RawArgs) -> None
        self._command = command
        self._raw_args = raw_args
        self._parsed_args = None
        self._parse_error = None
        self._parsed = False

    @property
    def command(self):  # type: () -> Command
        return self._command

    @property
    def raw_args(self):  # type: () -> RawArgs
        return self._raw_args

    @property
    def parsed_args(self):  # type: () -> Args
        if not self._parsed:
            self._parse()

        return self._parsed_args

    @property
    def parse_error(self):  # type: () -> CannotParseArgsException
        if not self._parsed:
            self._parse()

        return self._parse_error

    def is_parsable(self):  # type: () -> bool
        if not self._parsed:
            self._parse()

        return self.parse_error is None

    def _parse(self):  # type: () -> None
        try:
            self._parsed_args = self._command.parse(self._raw_args)
        except CannotParseArgsException as e:
            self._parse_error = e

        self._parsed = True
