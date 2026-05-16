"""LikeTableSeeder Seeder."""

from src.masoniteorm.models import Model
from src.masoniteorm.seeds import Seeder


class Like(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __table__ = "likes"


class LikeTableSeeder(Seeder):
    def run(self):
        """
        Seed the likes table for polymorphic relationship tests.

        test_can_get_polymorphic_relation and test_can_get_eager_load_polymorphic_relation
        iterate over all likes and assert each resolves to an Articles or User instance.
        The morph map is: {"user": User, "article": Articles}.
        """
        Like.bulk_create(
            [
                {"record_type": "article", "record_id": 1},
                {"record_type": "user", "record_id": 1},
                {"record_type": "user", "record_id": 2},
            ]
        )
