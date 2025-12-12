from clikit.api.args.args import Args
from clikit.api.io import IO


class HelpHandler:
    """
    Handler for the "help" command.
    """

    def handle(self, args, io):  # type: (Args, IO) -> int
        print(args)

        return 0
