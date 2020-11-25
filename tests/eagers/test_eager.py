import os
import unittest

from src.masoniteorm.query.EagerRelation import EagerRelations


class TestEagerRelation(unittest.TestCase):
    def test_can_register_string_eager_load(self):

        self.assertEqual(
            EagerRelations().register("profile").get_eagers(), [["profile"]]
        )
        self.assertEqual(EagerRelations().register("profile").is_nested, False)
        self.assertEqual(
            EagerRelations().register("profile.user").get_eagers(),
            [{"profile": ["user"]}],
        )
        self.assertEqual(
            EagerRelations().register("profile.user", "profile.logo").get_eagers(),
            [{"profile": ["user", "logo"]}],
        )
        self.assertEqual(
            EagerRelations()
            .register("profile.user", "profile.logo", "profile.bio")
            .get_eagers(),
            [{"profile": ["user", "logo", "bio"]}],
        )
        self.assertEqual(
            EagerRelations().register("user", "logo", "bio").get_eagers(),
            [["user", "logo", "bio"]],
        )

    def test_can_register_tuple_eager_load(self):

        self.assertEqual(
            EagerRelations().register(("profile",)).get_eagers(), [["profile"]]
        )
        self.assertEqual(
            EagerRelations().register(("profile", "user")).get_eagers(),
            [["profile", "user"]],
        )
        self.assertEqual(
            EagerRelations().register(("profile.name", "profile.user")).get_eagers(),
            [{"profile": ["name", "user"]}],
        )

    def test_can_register_list_eager_load(self):

        self.assertEqual(
            EagerRelations().register(["profile"]).get_eagers(), [["profile"]]
        )
        self.assertEqual(
            EagerRelations().register(["profile", "user"]).get_eagers(),
            [["profile", "user"]],
        )
        self.assertEqual(
            EagerRelations().register(["profile.name", "profile.user"]).get_eagers(),
            [{"profile": ["name", "user"]}],
        )
        self.assertEqual(
            EagerRelations().register(["profile.name"]).get_eagers(),
            [{"profile": ["name"]}],
        )
        self.assertEqual(
            EagerRelations().register(["profile.name", "logo"]).get_eagers(),
            [["logo"], {"profile": ["name"]}],
        )
        self.assertEqual(
            EagerRelations()
            .register(["profile.name", "logo", "profile.user"])
            .get_eagers(),
            [["logo"], {"profile": ["name", "user"]}],
        )
