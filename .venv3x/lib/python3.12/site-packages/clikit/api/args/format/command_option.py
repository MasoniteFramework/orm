import re

from typing import List
from typing import Optional

from .abstract_option import AbstractOption


class CommandOption(AbstractOption):
    """
    A command option in the console arguments.
    """

    def __init__(
        self, long_name, short_name=None, aliases=None, flags=0, description=None
    ):  # type: (str, Optional[str], Optional[List[str]], int, Optional[str]) -> None
        super(CommandOption, self).__init__(long_name, short_name, flags, description)

        if aliases is None:
            aliases = []

        self._long_aliases = []
        self._short_aliases = []

        for alias in aliases:
            alias = self._remove_dash_prefix(alias)

            if len(alias) == 1:
                self._validate_short_alias(alias)
                self._short_aliases.append(alias)
            else:
                self._validate_long_alias(alias)
                self._long_aliases.append(alias)

    @property
    def long_aliases(self):  # type: () -> List[str]
        return self._long_aliases

    @property
    def short_aliases(self):  # type: () -> List[str]
        return self._short_aliases

    def _validate_long_alias(self, alias):  # type: (str) -> None
        if not alias[:1].isalpha():
            raise ValueError("A long option alias must start with a letter.")

        if not re.match("^[a-zA-Z0-9\-]+$", alias):
            raise ValueError(
                "A long option alias must contain letters, digits and hyphens only."
            )

    def _validate_short_alias(self, alias):  # type: (str) -> None
        if not re.match("^[a-zA-Z]$", alias):
            raise ValueError(
                'A short option alias must be exactly one letter. Got: "{}"'.format(
                    alias
                )
            )
