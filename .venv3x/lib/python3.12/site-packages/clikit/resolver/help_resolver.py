from clikit.api.args.raw_args import RawArgs
from clikit.api.resolver import ResolvedCommand

from .default_resolver import DefaultResolver
from .resolve_result import ResolveResult


class HelpResolver(DefaultResolver):
    """
    A command resolver used by a help handler.
    """

    def __init__(self, help_command_name="help"):  # type: (str) -> None:
        self._help_command_name = help_command_name

    def resolve(
        self, args, application
    ):  # type: (RawArgs, Application) -> ResolvedCommand
        if args.tokens and args.tokens[0] == self._help_command_name:
            del args.tokens[0]

        return super(HelpResolver, self).resolve(args, application)

    def create_resolved_command(
        self, result
    ):  # type: (ResolveResult) -> ResolvedCommand
        result.command.config.enable_lenient_args_parsing()

        resolved_command = super(HelpResolver, self).create_resolved_command(result)

        result.command.config.disable_lenient_args_parsing()

        return resolved_command
