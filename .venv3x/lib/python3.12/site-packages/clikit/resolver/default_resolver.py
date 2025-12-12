from typing import Iterator
from typing import List
from typing import Optional

from clikit.api.args import RawArgs
from clikit.api.command import Command
from clikit.api.command import CommandCollection
from clikit.api.resolver import CommandResolver
from clikit.api.resolver import ResolvedCommand
from clikit.api.resolver.exceptions import CannotResolveCommandException

from .resolve_result import ResolveResult


class DefaultResolver(CommandResolver):
    """
    Parses the raw console arguments for the command to execute.
    """

    def resolve(
        self, args, application
    ):  # type: (RawArgs, Application) -> ResolvedCommand
        tokens = args.tokens
        named_commands = application.named_commands

        tokens = iter(tokens)
        arguments_to_test = self.get_arguments_to_test(tokens)
        options_to_test = self.get_options_to_test(tokens)

        result = self.process_arguments(
            args, named_commands, arguments_to_test, options_to_test
        )
        if result:
            return self.create_resolved_command(result)

        # Try to find a command for the passed arguments and options.
        if arguments_to_test:
            raise CannotResolveCommandException.name_not_found(
                arguments_to_test[0], named_commands
            )

        # If no arguments were passed, run the application's default command.
        result = self.process_default_commands(args, application.default_commands)
        if result:
            return self.create_resolved_command(result)

        raise CannotResolveCommandException.no_default_command()

    def process_arguments(
        self, args, named_commands, arguments_to_test, options_to_test
    ):  # type: (RawArgs, CommandCollection, List[str], List[str]) -> Optional[ResolveResult]
        current_command = None

        # Parse the arguments for command names until we fail to find a
        # matching command
        for name in arguments_to_test:
            if name not in named_commands:
                break

            next_command = named_commands.get(name)

            current_command = next_command
            named_commands = current_command.named_sub_commands

        if not current_command:
            return

        return self.process_options(args, current_command, options_to_test)

    def process_options(
        self, args, current_command, options_to_test
    ):  # type: (RawArgs, Command, List[str]) -> Optional[ResolveResult]
        for option in options_to_test:
            commands = current_command.named_sub_commands

            if option not in commands:
                continue

            next_command = commands.get(option)

        return self.process_default_sub_commands(args, current_command)

    def process_default_sub_commands(
        self, args, current_command
    ):  # type: (RawArgs, Command) -> Optional[ResolveResult]
        result = self.process_default_commands(
            args, current_command.default_sub_commands
        )

        if result:
            return result

        # No default commands, return the current command
        return ResolveResult(current_command, args)

    def process_default_commands(
        self, args, default_commands
    ):  # type: (RawArgs, CommandCollection) -> Optional[ResolveResult]
        first_result = None

        for default_command in default_commands:
            resolved_command = ResolveResult(default_command, args)

            if resolved_command.is_parsable():
                return resolved_command

            if not first_result:
                first_result = resolved_command

        # Return the first default command if one was found
        return first_result

    def get_arguments_to_test(self, tokens):  # type: (Iterator[str]) -> List[str]
        arguments_to_test = []
        token = next(tokens, None)

        while token:
            # "--" stops argument parsing
            if token == "--":
                break

            # Stop argument parsing when we reach the first option.

            # Command names must be passed before any option. The reason
            # is that we cannot determine whether an argument after an
            # option is the value of that option or an argument by itself
            # without getting the input definition of the corresponding
            # command first.

            # For example, in the command "server -f add" we don't know
            # whether "add" is the value of the "-f" option or an argument.
            # Hence we stop argument parsing after "-f" and assume that
            # "server" (or "server -f") is the command to execute.

            if token[:1] and token[0] == "-":
                break

            arguments_to_test.append(token)

            token = next(tokens, None)

        return arguments_to_test

    def get_options_to_test(self, tokens):  # type: (Iterator[str]) -> List[str]
        options_to_test = []
        token = next(tokens, None)

        while token:
            # "--" stops option parsing
            if token == "--":
                break

            if token[:1] and token[0] == "-":
                if token[:2] == "--" and len(token) > 2:
                    options_to_test.append(token[2:])
                elif len(token) == 2:
                    options_to_test.append(token[1:])

            token = next(tokens, None)

        return options_to_test

    def create_resolved_command(
        self, result
    ):  # type: (ResolveResult) -> ResolvedCommand
        if not result.is_parsable():
            raise result.parse_error

        return ResolvedCommand(result.command, result.parsed_args)
