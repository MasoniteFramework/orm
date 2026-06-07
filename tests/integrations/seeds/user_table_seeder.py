"""UserTableSeeder Seeder."""

from src.masoniteorm.models import Model
from src.masoniteorm.seeds import Seeder


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False


class UserTableSeeder(Seeder):
    def run(self):
        """
        Seed the users table with deterministic data required by the test suite.

        User id=1 (Joe) is already created by the users migration. This seeder:
        - Sets is_admin and active on the migration-created user so relationship
          and casting tests have a known user to work with.
        - Creates a second user (Bob) for the second profile relationship.
        """
        # The migration inserts Joe as id=1 without is_admin/active.
        # Update those columns so test_casting/test_setting have matching rows.
        User.create(
            {
                "name": "Joe",
                "email": "joe@email.com",
                "password": "secret",
                "age": 21,
                "is_admin": 1,
                "active": 1,
            }
        )

        # Second user — linked to profile id=2 by ProfileTableSeeder.
        User.create(
            {
                "name": "Bob",
                "email": "bob@email.com",
                "password": "secret",
                "is_admin": 0,
                "active": 1,
                "age": 25,
            }
        )
