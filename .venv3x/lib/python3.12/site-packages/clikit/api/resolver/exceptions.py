from clikit.api.exceptions import CliKitException
from clikit.utils.command import find_similar_command_names


class CannotResolveCommandException(RuntimeError, CliKitException):
    @classmethod
    def name_not_found(cls, name, commands):
        message = 'The command "{}" is not defined.'.format(name)

        suggested_names = find_similar_command_names(name, commands)

        if suggested_names:
            if len(suggested_names) == 1:
                message += "\n\nDid you mean this?\n    "
            else:
                message += "\n\nDid you mean one of these?\n    "

            message += "\n    ".join(suggested_names)

        return cls(message)

    @classmethod
    def no_default_command(cls):
        return cls("No default command is defined.")
