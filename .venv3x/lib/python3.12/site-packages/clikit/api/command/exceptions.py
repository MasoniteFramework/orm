from clikit.api.exceptions import CliKitException


class NoSuchCommandException(RuntimeError, CliKitException):
    def __init__(self, name):  # type: (str) -> None
        message = 'The command "{}" does not exist.'.format(name)

        super(NoSuchCommandException, self).__init__(message)


class CannotAddCommandException(RuntimeError):
    @classmethod
    def name_exists(cls, name):
        return cls('A command named "{}" already exists.'.format(name))

    @classmethod
    def option_exists(cls, name):
        return cls('A option named "{}" already exists.'.format(name))

    @classmethod
    def name_empty(cls):
        return cls("The command name must be set.")
