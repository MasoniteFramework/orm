"""ArticleTableSeeder Seeder."""

from src.masoniteorm.models import Model
from src.masoniteorm.seeds import Seeder


class Article(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __table__ = "articles"


class ArticleTableSeeder(Seeder):
    def run(self):
        """
        Seed the articles table.

        test_can_access_has_many_relationship asserts len(user(id=1).articles) == 1,
        so exactly one article linked to user_id=1 is required.
        test_associate_records hydrates Article(id=1), so the row id must be 1.
        published_date is used by test_can_access_relationship_date.
        """
        Article.create(
            {
                "user_id": 1,
                "title": "associate records",
                "published_date": "2020-11-28 11:42:07",
            }
        )
