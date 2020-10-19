import unittest

from databases.seeds.user_table_seeder import UserTableSeeder
from src.masoniteorm.seeds import Seeder


class TestSeeds(unittest.TestCase):
    def test_can_run_seeds(self):
        seeder = Seeder(dry=True)
        seeder.call(UserTableSeeder)

        self.assertEqual(seeder.ran_seeds, [UserTableSeeder])
