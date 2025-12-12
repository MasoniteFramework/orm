import itertools
import sys

from typing import List
from typing import Optional


from clikit.api.args.raw_args import RawArgs


class ArgvArgs(RawArgs):
    """
    Console arguments passed via sys.argv.
    """

    def __init__(self, argv=None):  # type: (Optional[List[str]]) -> None
        if argv is None:
            argv = list(sys.argv)

        argv = argv[:]
        self._script_name = argv.pop(0)
        self._tokens = argv
        self._option_tokens = list(
            itertools.takewhile(lambda arg: arg != "--", self.tokens)
        )

    @property
    def script_name(self):  # type: () -> str
        return self._script_name

    @property
    def tokens(self):  # type: () -> List[str]
        return self._tokens

    @property
    def option_tokens(self):  # type: () -> List[str]
        return self._option_tokens

    def has_token(self, token):  # type: (str) -> bool
        return token in self._tokens

    def has_option_token(self, token):  # type: (str) -> bool
        return token in self._option_tokens

    def to_string(self, script_name=True):  # type: (bool) -> str
        string = " ".join(self._tokens)

        if script_name:
            string = self._script_name.lstrip() + " " + string

        return string
