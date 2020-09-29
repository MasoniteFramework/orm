import unittest
from src.masoniteorm.seeds import Seeder
from databases.seeds.user_table_seeder import UserTableSeeder


class TestSeeds(unittest.TestCase):
    def test_can_run_seeds(self):
        seeder = Seeder(dry=True)
        seeder.call(UserTableSeeder)

        self.assertEqual(seeder.ran_seeds, [UserTableSeeder])
