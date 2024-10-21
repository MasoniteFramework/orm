import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import has_one_through
from tests.integrations.config.database import DATABASES
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform


class Port(Model):
    __table__ = "ports"
    __connection__ = "dev"
    __fillable__ = ["port_id", "name", "port_country_id"]


class Country(Model):
    __table__ = "countries"
    __connection__ = "dev"
    __fillable__ = ["country_id", "name"]


class IncomingShipment(Model):
    __table__ = "incoming_shipments"
    __connection__ = "dev"
    __fillable__ = ["shipment_id", "name", "from_port_id"]

    @has_one_through(None, "from_port_id", "port_country_id", "port_id", "country_id")
    def from_country(self):
        return [Country, Port]


class TestRelationships(unittest.TestCase):
    def setUp(self):
        self.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        with self.schema.create_table_if_not_exists("incoming_shipments") as table:
            table.integer("shipment_id").primary()
            table.string("name")
            table.integer("from_port_id")

        with self.schema.create_table_if_not_exists("ports") as table:
            table.integer("port_id").primary()
            table.string("name")
            table.integer("port_country_id")

        with self.schema.create_table_if_not_exists("countries") as table:
            table.integer("country_id").primary()
            table.string("name")

        if not Country.count():
            Country.builder.new().bulk_create(
                [
                    {"country_id": 10, "name": "Australia"},
                    {"country_id": 20, "name": "USA"},
                    {"country_id": 30, "name": "Canada"},
                    {"country_id": 40, "name": "United Kingdom"},
                ]
            )

        if not Port.count():
            Port.builder.new().bulk_create(
                [
                    {"port_id": 100, "name": "Melbourne", "port_country_id": 10},
                    {"port_id": 200, "name": "Darwin", "port_country_id": 10},
                    {"port_id": 300, "name": "South Louisiana", "port_country_id": 20},
                    {"port_id": 400, "name": "Houston", "port_country_id": 20},
                    {"port_id": 500, "name": "Montreal", "port_country_id": 30},
                    {"port_id": 600, "name": "Vancouver", "port_country_id": 30},
                    {"port_id": 700, "name": "Southampton", "port_country_id": 40},
                    {"port_id": 800, "name": "London Gateway", "port_country_id": 40},
                ]
            )

        if not IncomingShipment.count():
            IncomingShipment.builder.new().bulk_create(
                [
                    {"name": "Bread", "from_port_id": 300},
                    {"name": "Milk", "from_port_id": 100},
                    {"name": "Tractor Parts", "from_port_id": 100},
                    {"name": "Fridges", "from_port_id": 700},
                    {"name": "Wheat", "from_port_id": 600},
                    {"name": "Kettles", "from_port_id": 400},
                    {"name": "Bread", "from_port_id": 700},
                ]
            )

    def test_has_one_through_can_eager_load(self):
        shipments = IncomingShipment.where("name", "Bread").with_("from_country").get()
        self.assertEqual(shipments.count(), 2)

        shipment1 = shipments.shift()
        self.assertIsInstance(shipment1.from_country, Country)
        self.assertEqual(shipment1.from_country.country_id, 20)

        shipment2 = shipments.shift()
        self.assertIsInstance(shipment2.from_country, Country)
        self.assertEqual(shipment2.from_country.country_id, 40)

        # check .first() and .get() produce the same result
        single = (
            IncomingShipment.where("name", "Tractor Parts")
            .with_("from_country")
            .first()
        )
        single_get = (
            IncomingShipment.where("name", "Tractor Parts").with_("from_country").get()
        )
        self.assertEqual(single.from_country.country_id, 10)
        self.assertEqual(single_get.count(), 1)
        self.assertEqual(
            single.from_country.country_id, single_get.first().from_country.country_id
        )

    def test_has_one_through_eager_load_can_be_empty(self):
        shipments = (
            IncomingShipment.where("name", "Bread")
            .where_has("from_country", lambda query: query.where("name", "Ueaguay"))
            .with_(
                "from_country",
            )
            .get()
        )
        self.assertEqual(shipments.count(), 0)

    def test_has_one_through_can_get_related(self):
        shipment = IncomingShipment.where("name", "Milk").first()
        self.assertIsInstance(shipment.from_country, Country)
        self.assertEqual(shipment.from_country.country_id, 10)

    def test_has_one_through_has_query(self):
        shipments = IncomingShipment.where_has(
            "from_country", lambda query: query.where("name", "USA")
        )
        self.assertEqual(shipments.count(), 2)
