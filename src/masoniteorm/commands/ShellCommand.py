import subprocess
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

        command = self.get_command(config)
        if self.option("show"):
            self.comment(command)
            self.line("")

        # let shlex split command in a list as it's safer
        command_args = shlex.split(command)
        try:
            subprocess.run(command_args, check=True)
        except FileNotFoundError:
            self.line(
                f"<error>Cannot find {config.get('full_details').get('driver')} program ! Please ensure you can call this program in your shell first.</error>"
            )
            exit(-1)

    def get_shell_program(self, connection):
        """Get the database shell program to run."""
        return self.shell_programs.get(connection)

    def get_command(self, config):
        """Get the command to run as a string."""
        driver = config.get("full_details").get("driver")
        program = self.get_shell_program(driver)
        try:
            args, options = getattr(self, f"get_{driver}_args")(config)
        except AttributeError:
            self.line(
                f"<error>Connecting with driver '{driver}' is not implemented !</error>"
            )
            exit(-1)
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
        return command

    def get_mysql_args(self, config):
        """Get command positional arguments and options for MySQL driver."""
        args = [config.get("database")]
        options = OrderedDict(
            {
                "--host": config.get("host"),
                "--port": config.get("port"),
                "--user": config.get("user"),
                "--password": config.get("password"),
                "--default-character-set": config.get("options").get("charset"),
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
                "--password": config.get("password"),
            }
        )
        return args, options

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
                "-t": config.get("options").get("connection_timeout"),
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
