"""ProfileTableSeeder Seeder."""

from src.masoniteorm.models import Model
from src.masoniteorm.seeds import Seeder


class Profile(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __table__ = "profiles"


class ProfileTableSeeder(Seeder):
    def run(self):
        """
        Seed the profiles table.

        test_can_access_relationship asserts User(id=1).profile is a Profile instance.
        test_with asserts profile.title == 'title'.
        Two profiles are required: one for each seeded user.
        """
        Profile.bulk_create(
            [
                {"user_id": 1, "title": "title"},
                {"user_id": 2, "title": "title"},
            ]
        )
