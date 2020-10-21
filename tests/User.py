""" User Model """

from src.masoniteorm import Model


class User(Model):
    """User Model"""

    __fillable__ = ["name", "email", "password"]

    __connection__ = "mysql"

    __auth__ = "email"

    @property
    def meta(self):
        return 1
