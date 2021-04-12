from masonite.providers import Provider

from masoniteorm.commands import (
    MakeMigrationCommand,
    MakeSeedCommand,
    MakeObserverCommand,
    MigrateCommand,
    MigrateRefreshCommand,
    MigrateRollbackCommand,
    SeedRunCommand,
)


class ORMProvider(Provider):
    """Masonite ORM database provider to be used inside
    Masonite based projects."""

    def __init__(self, application):
        self.application = application

    def register(self):
        self.application.make("commands").add(
            MakeMigrationCommand(),
            MakeSeedCommand(),
            MakeObserverCommand(),
            MigrateCommand(),
            MigrateRefreshCommand(),
            MigrateRollbackCommand(),
            SeedRunCommand(),
        ),

    def boot(self):
        pass
