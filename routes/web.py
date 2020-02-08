""" Web Routes """
from masonite.routes import Get, Post

ROUTES = [
    Get('/', 'PackageController@show').name('welcome'),
]
