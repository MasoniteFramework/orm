"""Craft Command.

This module is really used for backup only if the masonite CLI cannot import this for you.
This can be used by running "python craft". This module is not ran when the CLI can
successfully import commands for you.
"""

from cleo import Application

from . import (
    MakeMigrationCommand,
    MakeModelCommand,
    MakeModelDocstringCommand,
    MakeObserverCommand,
    MakeSeedCommand,
    MigrateCommand,
    MigrateFreshCommand,
    MigrateRefreshCommand,
    MigrateResetCommand,
    MigrateRollbackCommand,
    MigrateStatusCommand,
    SeedRunCommand,
    ShellCommand,
)

application = Application("ORM Version:", 0.1)

application.add(MigrateCommand())
application.add(MigrateRollbackCommand())
application.add(MigrateRefreshCommand())
application.add(MigrateFreshCommand())
application.add(MakeMigrationCommand())
application.add(MakeModelCommand())
application.add(MakeModelDocstringCommand())
application.add(MakeObserverCommand())
application.add(MigrateResetCommand())
application.add(MigrateStatusCommand())
application.add(MakeSeedCommand())
application.add(SeedRunCommand())
application.add(ShellCommand())

if __name__ == "__main__":
    application.run()
