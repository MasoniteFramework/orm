"""LogoTableSeeder Seeder."""

from src.masoniteorm.models import Model
from src.masoniteorm.seeds import Seeder


class Logo(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __table__ = "logos"


class LogoTableSeeder(Seeder):
    def run(self):
        """
        Seed the logos table.

        test_can_access_relationship_date calls article.logo.published_date.is_past(),
        so a logo linked to article_id=1 with a past published_date is required.
        test_loading_with_nested_with uses the nested 'articles.logo' eager load.
        """
        Logo.create(
            {
                "article_id": 1,
                "url": "google.com",
                "published_date": "2020-11-28 11:42:07",
            }
        )
