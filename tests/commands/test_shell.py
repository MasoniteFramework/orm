import unittest
from cleo import CommandTester

from src.masoniteorm.commands import ShellCommand


class TestShellCommand(unittest.TestCase):
    def setUp(self):
        self.command = ShellCommand()
        self.command_tester = CommandTester(self.command)

    def test_for_mysql(self):
        config = {
            "host": "localhost",
            "database": "orm",
            "user": "root",
            "port": "1234",
            "password": "secret",
            "prefix": "",
            "options": {"charset": "utf8mb4"},
            "full_details": {"driver": "mysql"},
        }
        command, _ = self.command.get_command(config)
        assert (
            command
            == "mysql orm --host localhost --port 1234 --user root --password secret --default-character-set utf8mb4"
        )

    def test_for_postgres(self):
        config = {
            "host": "localhost",
            "database": "orm",
            "user": "root",
            "port": "1234",
            "password": "secretpostgres",
            "prefix": "",
            "options": {"charset": "utf8mb4"},
            "full_details": {"driver": "postgres"},
        }
        command, env = self.command.get_command(config)
        assert command == "psql orm --host localhost --port 1234 --username root"
        assert env.get("PGPASSWORD", "secretpostgres")

    def test_for_sqlite(self):
        config = {
            "database": "orm.sqlite3",
            "prefix": "",
            "full_details": {"driver": "sqlite"},
        }
        command, _ = self.command.get_command(config)
        assert command == "sqlite3 orm.sqlite3"

    def test_for_mssql(self):
        config = {
            "host": "db.masonite.com",
            "database": "orm",
            "user": "root",
            "port": "1234",
            "password": "secretpostgres",
            "prefix": "",
            "options": {"charset": "utf8mb4"},
            "full_details": {"driver": "mssql"},
        }
        command, _ = self.command.get_command(config)
        assert (
            command
            == "sqlcmd -d orm -U root -P secretpostgres -S tcp:db.masonite.com,1234"
        )

    def test_running_command_with_sqlite(self):
        self.command_tester.execute("-c dev")
        assert "sqlite3" not in self.command_tester.io.fetch_output()
        self.command_tester.execute("-c dev -s")
        assert "sqlite3 orm.sqlite3" in self.command_tester.io.fetch_output()

    def test_hiding_sensitive_options(self):
        config = {
            "host": "localhost",
            "database": "orm",
            "user": "root",
            "port": "",
            "password": "secret",
            "full_details": {"driver": "mysql"},
        }
        command, _ = self.command.get_command(config)
        cleaned_command = self.command.hide_sensitive_options(config, command)
        assert (
            cleaned_command == "mysql orm --host localhost --user root --password ***"
        )
