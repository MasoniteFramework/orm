from masonite.provider import ServiceProvider
from masonite.helpers import config

from masoniteorm.connections import ConnectionResolver
from masoniteorm.commands import (
    MakeMigrationCommand,
    MakeSeedCommand,
    MigrateCommand,
    MigrateRefreshCommand,
    MigrateRollbackCommand,
    SeedRunCommand,
)


class ORMProvider(ServiceProvider):
    """Masonite ORM database provider to be used inside
    Masonite based projects."""

    wsgi = False

    def register(self):
        self.commands(
            MakeMigrationCommand(),
            MakeSeedCommand(),
            MigrateCommand(),
            MigrateRefreshCommand(),
            MigrateRollbackCommand(),
            SeedRunCommand(),
        )

    def boot(self):
        pass
