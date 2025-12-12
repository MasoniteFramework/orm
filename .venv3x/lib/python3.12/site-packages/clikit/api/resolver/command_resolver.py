from clikit.api.args import RawArgs

from .resolved_command import ResolvedCommand


class CommandResolver(object):
    """
    Returns the command to execute for the given console arguments.
    """

    def resolve(
        self, args, application
    ):  # type: (RawArgs, Application) -> ResolvedCommand
        raise NotImplementedError()
