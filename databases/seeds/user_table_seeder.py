"""UserTableSeeder Seeder."""

from src.masonite.orm.seeds import Seeder
from src.masonite.orm.factories import Factory as factory
from app.User import User

factory.register(User, lambda faker: {'email': faker.email()})

class UserTableSeeder(Seeder):

    def run(self):
        """Run the database seeds."""
        factory(User, 5).create({
            'name': 'Joe',
            'password': 'joe',
        })
