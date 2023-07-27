from masoniteorm.exceptions import DriverNotFound


class MySQLSingleConnection:
    def __init__(self):
        self.transaction_level = 0
        self._connection = None

    def connect(self, **kwargs):
        try:
            import pymysql
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'pymysql' package installed to make a connection to MySQL. Please install it using "
                "'pip install pymysql'"
            )
        try:
            import pendulum
            import pymysql.converters
            pymysql.converters.conversions[
                pendulum.DateTime
            ] = pymysql.converters.escape_datetime
        except ImportError:
            pass

        self._connection = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor,
            **kwargs
        )

    def reconnect(self):
        return self._connection.connect()

    def cursor(self):
        return self._connection.cursor()

    def commit(self):
        """Transaction"""
        return self._connection.commit()

    def begin(self):
        """Mysql Transaction"""
        return self._connection.begin()

    def rollback(self):
        """Transaction"""
        return self._connection.rollback()
