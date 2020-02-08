""" Welcome The User To Masonite """

from masonite.view import View
from masonite.request import Request
from app.User import User

class PackageController:
    """Controller For Welcoming The User
    """

    def show(self, view: View, request: Request):

        return 'Hello World'
