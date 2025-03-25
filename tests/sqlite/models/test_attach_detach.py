import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, has_one
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


class Bottle(Model):
    __table__ = "bottles"
    __connection__ = "dev"
    __timestamps__ = False
    __fillable__ = ["label"]

    @has_one(None, "bottle_id", "id")
    def lid(self):
        return BottleLid


class BottleLid(Model):
    __table__ = "bottle_lids"
    __connection__ = "dev"
    __timestamps__ = False
    __fillable__ = ["colour", "bottle_id"]

    @belongs_to(None, "bottle_id", "id")
    def bottle(self):
        return Bottle


class TestAttachDetach(unittest.TestCase):
    def setUp(self):
        self.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        with self.schema.create_table_if_not_exists("bottles") as table:
            table.integer("id").primary()
            table.string("label")

        with self.schema.create_table_if_not_exists("bottle_lids") as table:
            table.integer("id").primary()
            table.string("colour")
            table.integer("bottle_id", nullable=True)  # HasOne / BelongsTo relationship

    def tearDown(self):
        BottleLid.delete()
        Bottle.delete()

    def test_has_one_attach_detach(self):
        bottle = Bottle.create(
            {
                "label": "cola",
            }
        )

        # test unsaved
        red_lid = BottleLid().fill(
            {
                "colour": "Red",
            }
        )
        current_lid = bottle.attach("lid", red_lid)
        self.assertIsNotNone(bottle.lid)
        self.assertIsInstance(current_lid, BottleLid)
        self.assertTrue(current_lid.is_created())
        self.assertEqual(bottle.id, current_lid.bottle_id)

        bottle.detach("lid", current_lid)
        test_lid = BottleLid.find(current_lid.id)
        self.assertIsNone(test_lid.bottle_id)
        self.assertIsNone(bottle.lid)

        # test usning a pre-saved record
        green_lid = BottleLid.create(
            {
                "colour": "Green",
            }
        )
        current_lid = bottle.attach("lid", green_lid)
        self.assertIsNotNone(bottle.lid)
        self.assertIsInstance(current_lid, BottleLid)
        self.assertEqual(bottle.id, current_lid.bottle_id)

        bottle.detach("lid", current_lid)
        test_lid = BottleLid.find(current_lid.id)
        self.assertIsNone(test_lid.bottle_id)
        self.assertIsNone(bottle.lid)

    def test_belongs_to_attach_detach(self):
        bottle = Bottle.create(
            {
                "label": "milk",
            }
        )

        # test unsaved
        red_lid = BottleLid().fill(
            {
                "colour": "Red",
            }
        )
        current_lid = red_lid.attach("bottle", bottle)
        self.assertIsNotNone(bottle.lid)
        self.assertIsInstance(current_lid, BottleLid)
        self.assertTrue(current_lid.is_created())
        self.assertEqual(bottle.id, current_lid.bottle_id)

        current_lid.detach("bottle", bottle)
        test_lid = BottleLid.find(current_lid.id)
        self.assertIsNone(test_lid.bottle_id)
        self.assertIsNone(bottle.lid)

        # test usning a pre-saved record
        green_lid = BottleLid.create(
            {
                "colour": "Green",
            }
        )
        current_lid = green_lid.attach("bottle", bottle)
        self.assertIsNotNone(bottle.lid)
        self.assertIsInstance(current_lid, BottleLid)
        self.assertEqual(bottle.id, current_lid.bottle_id)

        current_lid.detach("bottle", bottle)
        test_lid = BottleLid.find(current_lid.id)
        self.assertIsNone(test_lid.bottle_id)
        self.assertIsNone(bottle.lid)
