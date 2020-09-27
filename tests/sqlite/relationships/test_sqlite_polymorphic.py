import os
import unittest

from src.masoniteorm.orm.models import Model
from src.masoniteorm.orm.relationships import belongs_to, has_many, morph_to


class Profile(Model):
    __table__ = "profiles"
    __connection__ = "sqlite"


class Articles(Model):
    __table__ = "articles"
    __connection__ = "sqlite"

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo


class Logo(Model):
    __table__ = "logos"
    __connection__ = "sqlite"


class Like(Model):

    __connection__ = "sqlite"

    @morph_to("record_type", "record_id")
    def record(self):
        return self


class User(Model):

    __connection__ = "sqlite"

    _eager_loads = ()


morph_to.set_morph_map({"user": User, "article": Articles})


class TestRelationships(unittest.TestCase):
    maxDiff = None

    def test_can_get_polymorphic_relation(self):
        likes = Like.get()
        for like in likes:
            self.assertIsInstance(like.record, (Articles, User))
