import subprocess
import os
import re
import shlex
from collections import OrderedDict

from ..config import load_config

from .Command import Command


class ShellCommand(Command):
    """
    Connect to your database interactive terminal.

    shell
        {--c|connection=default : The connection you want to use to connect to interactive terminal}
        {--s|show=? : Display the command which will be called to connect}
    """

    shell_programs = {
        "mysql": "mysql",
        "postgres": "psql",
        "sqlite": "sqlite3",
        "mssql": "sqlcmd",
    }

    def handle(self):
        resolver = load_config(self.option("config")).DB
        connection = self.option("connection")
        if connection == "default":
            connection = resolver.get_connection_details()["default"]
        config = resolver.get_connection_information(connection)
        if not config.get("full_details"):
            self.line(
                f"<error>Connection configuration for '{connection}' not found !</error>"
            )
            exit(-1)

        command, env = self.get_command(config)

        if self.option("show"):
            cleaned_command = self.hide_sensitive_options(config, command)
            self.comment(cleaned_command)
            self.line("")

        # let shlex split command in a list as it's safer
        command_args = shlex.split(command)
        try:
            subprocess.run(command_args, check=True, env=env)
        except FileNotFoundError:
            self.line(
                f"<error>Cannot find {config.get('full_details').get('driver')} program ! Please ensure you can call this program in your shell first.</error>"
            )
            exit(-1)
        except subprocess.CalledProcessError:
            self.line(f"<error>An error happened calling the command.</error>")
            exit(-1)

    def get_shell_program(self, connection):
        """Get the database shell program to run."""
        return self.shell_programs.get(connection)

    def get_command(self, config):
        """Get the command to run as a string."""
        driver = config.get("full_details").get("driver")
        program = self.get_shell_program(driver)
        try:
            get_driver_args = getattr(self, f"get_{driver}_args")
        except AttributeError:
            self.line(
                f"<error>Connecting with driver '{driver}' is not implemented !</error>"
            )
            exit(-1)
        args, options = get_driver_args(config)
        # process positional arguments
        args = " ".join(args)
        # process optional arguments
        options = self.remove_empty_options(options)
        options_string = " ".join(
            f"{option} {value}" if value else option
            for option, value in options.items()
        )
        # finally build command string
        command = program
        if args:
            command += f" {args}"
        if options_string:
            command += f" {options_string}"

        # prepare environment in which command will be run
        # some drivers need to define env variable such as psql for specifying password
        try:
            driver_env = getattr(self, f"get_{driver}_env")(config)
        except AttributeError:
            driver_env = {}
        command_env = {**os.environ.copy(), **driver_env}

        return command, command_env

    def get_mysql_args(self, config):
        """Get command positional arguments and options for MySQL driver."""
        args = [config.get("database")]
        options = OrderedDict(
            {
                "--host": config.get("host"),
                "--port": config.get("port"),
                "--user": config.get("user"),
                "--password": config.get("password"),
                "--default-character-set": config.get("options", {}).get("charset"),
            }
        )
        return args, options

    def get_postgres_args(self, config):
        """Get command positional arguments and options for PostgreSQL driver."""
        args = [config.get("database")]
        options = OrderedDict(
            {
                "--host": config.get("host"),
                "--port": config.get("port"),
                "--username": config.get("user"),
            }
        )
        return args, options

    def get_postgres_env(self, config):
        return {"PGPASSWORD": config.get("password")}

    def get_mssql_args(self, config):
        """Get command positional arguments and options for MSSQL driver."""
        args = []

        # instance of SQL Server: -S [protocol:]server[instance_name][,port]
        server = f"tcp:{config.get('host')}"
        if config.get("port"):
            server += f",{config.get('port')}"

        trusted_connection = config.get("options").get("trusted_connection") == "Yes"
        options = OrderedDict(
            {
                "-d": config.get("database"),
                "-U": config.get("user"),
                "-P": config.get("password"),
                "-S": server,
                "-E": trusted_connection,
                "-t": config.get("options", {}).get("connection_timeout"),
            }
        )
        return args, options

    def get_sqlite_args(self, config):
        """Get command positional arguments and options for SQLite driver."""
        args = [config.get("database")]
        options = OrderedDict()
        return args, options

    def remove_empty_options(self, options):
        """Remove empty options when value does not evaluate to True.
        Also when value is exactly 'True' we don't want True to be passed as option value but
        we want the option to be passed.
        """
        # remove empty options and remove value when option is True
        cleaned_options = OrderedDict()
        for key, value in options.items():
            if value is True:
                cleaned_options[key] = ""
            elif value:
                cleaned_options[key] = value
        return cleaned_options

    def get_sensitive_options(self, config):
        driver = config.get("full_details").get("driver")
        try:
            sensitive_options = getattr(self, f"get_{driver}_sensitive_options")()
        except AttributeError:
            sensitive_options = []
        return sensitive_options

    def get_mysql_sensitive_options(self):
        return ["--password"]

    def get_mssql_sensitive_options(self):
        return ["-P"]

    def hide_sensitive_options(self, config, command):
        """Hide sensitive options in command string before it's displayed in the shell for
        security reasons. All drivers can declare what options are considered sensitive, their
        values will be then replaced by *** when displayed only."""
        cleaned_command = command
        sensitive_options = self.get_sensitive_options(config)
        for option in sensitive_options:
            # if option is used obfuscate its value
            if option in command:
                match = re.search(rf"{option} (\w+)", command)
                if match.groups():
                    cleaned_command = cleaned_command.replace(match.groups()[0], "***")
        return cleaned_command
