""" User Model """

from config.database import Model
from src.masonite.orm.models.Model import Model


class User(Model):
    """User Model 
    """

    __fillable__ = ['name', 'email', 'password']

    __connection__ = 'mysql'

    __auth__ = 'email'
