"""
Pytest configuration for tests/sqlite/.

Ensures a clean, fully-migrated SQLite database before each test session by
running the integration migrations and seeds from tests/integrations/.

Scoped to this directory intentionally — other test suites (mysql, postgres,
mssql) manage their own connections and do not need SQLite setup.
"""

import os
import pathlib

import pytest

# Set config path before any ORM import so load_config() picks it up.
# Tests that import from tests.integrations.config.database build their own
# ConnectionResolver directly, so they are unaffected by this setting.
os.environ.setdefault("DB_CONFIG_PATH", "tests/integrations/config/database")

from src.masoniteorm.migrations import Migration  # noqa: E402
from tests.integrations.seeds.database_seeder import (  # noqa: E402
    DatabaseSeeder,
)

_SQLITE_DB = pathlib.Path("orm.sqlite3")
_MIGRATION_DIR = "tests/integrations/migrations"
_CONNECTION = "dev"


@pytest.fixture(scope="session", autouse=True)
def sqlite_db_session():
    """
    Session-scoped fixture that resets the SQLite database, runs all
    integration migrations, then seeds initial data.

    Runs exactly once per pytest session, before the first test in
    tests/sqlite/ executes. The autouse=True + conftest placement means every
    test in this directory receives a consistently-seeded database without
    needing to import or reference this fixture explicitly.

    Individual tests that need isolated state (e.g. test_attach_detach) manage
    their own setUp/tearDown as normal — this fixture only establishes the base
    schema and seed data those tests build on top of.
    """
    _reset_db()
    _run_migrations()
    _run_seeds()
    yield
    # Leave the file in place for post-run inspection.
    # The next session will reset it via _reset_db().


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_db() -> None:
    """Delete the SQLite file so every session starts from a clean slate."""
    if _SQLITE_DB.exists():
        _SQLITE_DB.unlink()


def _run_migrations() -> None:
    """
    Run all unran migrations from tests/integrations/migrations/ against the
    'dev' (SQLite) connection.

    Migration.create_table_if_not_exists() is called first to bootstrap the
    migrations tracking table on a fresh database.
    """
    migration = Migration(
        connection=_CONNECTION,
        migration_directory=_MIGRATION_DIR,
    )
    migration.create_table_if_not_exists()
    migration.migrate()


def _run_seeds() -> None:
    """
    Run the DatabaseSeeder from tests/integrations/seeds/.

    DatabaseSeeder.run() delegates to each registered sub-seeder (e.g.
    UserTableSeeder) in order, so adding new seeders only requires updating
    DatabaseSeeder — not this conftest.
    """
    DatabaseSeeder(connection=_CONNECTION).run()
