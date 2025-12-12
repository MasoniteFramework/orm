import itertools

from typing import List
from typing import Optional


from clikit.api.args import RawArgs

from .token_parser import TokenParser


class StringArgs(RawArgs):
    """
    Console arguments passed as a string.
    """

    def __init__(self, string):  # type: (str) -> None
        parser = TokenParser()

        self._tokens = parser.parse(string)
        self._option_tokens = list(
            itertools.takewhile(lambda arg: arg != "--", self.tokens)
        )

    @property
    def script_name(self):  # type: () -> Optional[str]
        return

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
        return " ".join(self._tokens)
