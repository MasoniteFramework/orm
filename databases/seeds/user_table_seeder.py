"""UserTableSeeder Seeder."""

from src.masoniteorm.seeds import Seeder
from src.masoniteorm.factories import Factory as factory
from tests.User import User

factory.register(User, lambda faker: {'email': faker.email()})

class UserTableSeeder(Seeder):

    def run(self):
        """Run the database seeds."""
        factory(User, 5).create({
            'name': 'Joe',
            'password': 'joe',
        })
