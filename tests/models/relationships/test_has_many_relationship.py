import unittest
from src.masoniteorm.models import Model

class User(Model):
    __connection__ = "t"

    @property
    def articles(self):
        return self.has_many(Article, "id", "user_id")
    
class Article(Model):
    __connection__ = "t"





class TestHasManyRelatinship(unittest.TestCase):

    def test_can_get_owner_value(self):
        user = User.find(1)
        self.assertEqual(user.name, "bill")

    def test_can_get_has_many_related_value(self):
        user = User.find(1)
        for article in user.articles:
            self.assertEqual(article.title, "masonite")
            self.assertEqual(user.articles.first().title, "masonite")

    def test_can_get_has_many_query_builder(self):
        user = User.find(1)
        self.assertEqual(user.name, "bill")
        self.assertEqual(user.articles().to_sql(), 'SELECT * FROM "articles" WHERE "articles"."user_id" = \'1\'')

    def test_can_get_eager_load_from_builder(self):
        user = User.with_("articles").find(1)
        self.assertEqual(user.name, "bill")
        self.assertEqual(user.articles.first().title, 'masonite')

    # def test_can_get_nested_eager_load_from_builder(self):
    #     user = User.with_("articles.user").find(1)
    #     self.assertEqual(user.profile.user.name, "bill")
    #     self.assertEqual(user.profile.user.name, "bill")