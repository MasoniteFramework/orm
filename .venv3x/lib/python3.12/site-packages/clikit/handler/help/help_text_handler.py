from clikit.api.args import Args
from clikit.api.command import Command
from clikit.api.io import IO
from clikit.api.resolver import CommandResolver

from clikit.ui.help import ApplicationHelp
from clikit.ui.help import CommandHelp


class HelpTextHandler:
    """
    Displays help as text format.
    """

    def __init__(self, resolver):  # type: (CommandResolver) -> None
        self._resolver = resolver

    def handle(self, args, io, command):  # type: (Args, IO, Command) -> int
        application = command.application

        if args.is_argument_set("command"):
            resolved_command = self._resolver.resolve(args.raw_args, application)
            the_command = resolved_command.command

            usage = CommandHelp(the_command)
        else:
            usage = ApplicationHelp(application)

        usage.render(io)

        return 0
