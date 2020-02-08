""" CSRF Middleware """

from masonite.middleware import CsrfMiddleware as Middleware


class CsrfMiddleware(Middleware):
    """ Verify CSRF Token Middleware """

    exempt = [
        '/api/user',
        '/token',
        '/jwt',
        '/jwt/refresh',
        '/authorize'
    ]
