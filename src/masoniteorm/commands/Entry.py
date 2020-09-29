"""Craft Command.

This module is really used for backup only if the masonite CLI cannot import this for you.
This can be used by running "python craft". This module is not ran when the CLI can
successfully import commands for you.
"""

from cleo import Application
from . import (
    MigrateCommand,
    MigrateRollbackCommand,
    MigrateRefreshCommand,
    MakeMigrationCommand,
    MakeSeedCommand,
    SeedRunCommand,
)

from wsgi import container

application = Application("ORM Version:", 0.1)

application.add(MigrateCommand())
application.add(MigrateRollbackCommand())
application.add(MigrateRefreshCommand())
application.add(MakeMigrationCommand())
application.add(MakeSeedCommand())
application.add(SeedRunCommand())

if __name__ == "__main__":
    application.run()
