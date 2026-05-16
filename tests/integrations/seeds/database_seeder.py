"""Base Database Seeder Module."""

from src.masoniteorm.seeds import Seeder

from .article_table_seeder import ArticleTableSeeder
from .like_table_seeder import LikeTableSeeder
from .logo_table_seeder import LogoTableSeeder
from .profile_table_seeder import ProfileTableSeeder
from .store_table_seeder import StoreTableSeeder
from .user_table_seeder import UserTableSeeder


class DatabaseSeeder(Seeder):
    def run(self):
        """
        Run all database seeds in dependency order.

        Users must be seeded before profiles, articles, and likes since those
        tables reference user IDs. Articles must exist before logos.
        Stores and products are independent of the user graph.
        """
        self.call(
            UserTableSeeder,
            ProfileTableSeeder,
            ArticleTableSeeder,
            LogoTableSeeder,
            LikeTableSeeder,
            StoreTableSeeder,
        )
