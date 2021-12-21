from cleo import Command


class CanOverrideConfig(Command):
    def __init__(self):
        super().__init__()
        self.add_option()

    def add_option(self):
        # 8 is the required flag constant in cleo
        self._config.add_option(
            "config",
            "C",
            8,
            description="The path to the ORM configuration file. If not given DB_CONFIG_PATH env variable will be used and finally 'config.database'.",
        )
