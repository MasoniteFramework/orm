from typing import List

from clikit.utils._compat import OrderedDict

from .command import Command
from .exceptions import NoSuchCommandException


class CommandCollection(object):
    """
    A collection of named commands.
    """

    def __init__(self, commands=None):  # type: (List[Command]) -> None
        if commands is None:
            commands = []

        self._commands = OrderedDict()
        self._short_name_index = OrderedDict()
        self._alias_index = OrderedDict()

        for command in commands:
            self.add(command)

    def add(self, command):  # type: (Command) -> CommandCollection
        name = command.name

        self._commands[name] = command

        short_name = command.short_name
        if short_name:
            self._short_name_index[short_name] = name

        for alias in command.aliases:
            self._alias_index[alias] = name

        return self

    def get(self, name):  # type: (str) -> Command
        if name in self._commands:
            return self._commands[name]

        if name in self._short_name_index:
            return self._commands[self._short_name_index[name]]

        if name in self._alias_index:
            return self._commands[self._alias_index[name]]

        raise NoSuchCommandException(name)

    def is_empty(self):  # type: () -> bool
        return not self._commands

    def get_names(self, include_aliases=False):  # type: (bool) -> List[str]
        names = list(self._commands.keys())

        if include_aliases:
            names += list(self._alias_index.keys())

        names.sort()

        return names

    def __contains__(self, name):
        return (
            name in self._commands
            or name in self._short_name_index
            or name in self._alias_index
        )

    def __iter__(self):
        return iter(self._commands.values())

    def __len__(self):
        return len(self._commands)
