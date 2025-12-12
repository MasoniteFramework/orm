from clikit.api.exceptions import CliKitException


class CannotAddOptionException(RuntimeError):
    @classmethod
    def already_exists(cls, name):
        return cls(
            'An option named "{}{}" exists already.'.format(
                "--" if len(name) > 1 else "-", name
            )
        )


class NoSuchOptionException(RuntimeError):
    def __init__(self, name):
        message = 'The "{}{}" option does not exist.'.format(
            "--" if len(name) > 1 else "-", name
        )

        super(NoSuchOptionException, self).__init__(message)


class CannotAddArgumentException(RuntimeError):
    @classmethod
    def already_exists(cls, name):
        return cls('An argument named "{}" exists already.'.format(name))

    @classmethod
    def cannot_add_after_multi_valued(cls):
        return cls("Cannot add an argument after a multi-valued argument.")

    @classmethod
    def cannot_add_required_after_optional(cls):
        return cls("Cannot add a required argument after an optional one.")


class NoSuchArgumentException(RuntimeError):
    def __init__(self, name):
        if isinstance(name, int):
            message = "The argument at position {} does not exist.".format(name)
        else:
            message = 'The "{}" argument does not exist.'.format(name)

        super(NoSuchArgumentException, self).__init__(message)


class CannotParseArgsException(RuntimeError, CliKitException):
    @classmethod
    def too_many_arguments(cls):
        return cls("Too many arguments.")

    @classmethod
    def option_does_not_accept_value(cls, name):
        if len(name) > 1:
            name = "--" + name
        else:
            name = "--" + name

        return cls('The "{}" option does not accept a value.'.format(name))

    @classmethod
    def option_requires_value(cls, name):
        if len(name) > 1:
            name = "--" + name
        else:
            name = "--" + name

        return cls('The "{}" option requires a value.'.format(name))
