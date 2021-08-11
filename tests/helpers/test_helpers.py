import unittest
from src.masoniteorm.helpers import database_url

class TestHelper(unittest.TestCase):

    def test_database_url(self):
        connection = database_url("mysql://user:secret@localhost:5432/mydatabasename")
        self.assertEqual(connection.get('user'), 'user')
        self.assertEqual(connection.get('password'), 'secret')
        self.assertEqual(connection.get('host'), 'localhost')
        self.assertEqual(connection.get('port'), '5432')
        self.assertEqual(connection.get('database'), 'mydatabasename')

    def test_database_url_no_database(self):
        connection = database_url("postgres://utpcrbiihfqqys:de0a0d847094a66e32274262aa5b5f0ad78e5e34197875fc6089a2d9185d0032@ec2-54-225-242-183.compute-1.amazonaws.com:5432/da455n1ef8kout")
        print(connection)
