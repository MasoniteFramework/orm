from typing import List
from typing import Optional


class CommandName(object):
    """
    A command name in the console arguments.
    """

    def __init__(
        self, string, aliases=None
    ):  # type: (str, Optional[List[str]]) -> None
        if aliases is None:
            aliases = []

        self._string = string
        self._aliases = aliases

    @property
    def string(self):  # type: () -> str
        return self._string

    @property
    def aliases(self):  # type: () -> List[str]
        return self._aliases

    def match(self, string):  # type: (str) -> bool
        return self._string == string or string in self._aliases

    def __str__(self):  # type: () -> str
        return self._string

    def __repr__(self):  # type: () -> str
        return 'CommandName("{}")'.format(self._string)
