from cleo.commands.command import Command


class CanOverrideConfig(Command):
    def __init__(self):
        super().__init__()
        self.add_option()

    def add_option(self):
        self._config.add_option(
            "option", "o", 8, "The location of the config module", None
        )

