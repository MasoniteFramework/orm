import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import (
    has_one_through,
)
from dotenv import load_dotenv

load_dotenv(".env")


class InboundShipment(Model):
    @has_one_through(None, "from_port_id", "country_id", "port_id", "country_id")
    def from_country(self):
        return Country, Port


class Country(Model):
    pass


class Port(Model):
    pass


class MySQLHasOneThroughRelationship(unittest.TestCase):
    maxDiff = None

    def test_has_query(self):
        sql = InboundShipment.has("from_country").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `inbound_shipments` WHERE EXISTS (SELECT * FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id`)""",
        )

    def test_or_has(self):
        sql = InboundShipment.where("name", "Joe").or_has("from_country").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `inbound_shipments` WHERE `inbound_shipments`.`name` = 'Joe' OR EXISTS (SELECT * FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id`)""",
        )

    def test_where_has_query(self):
        sql = InboundShipment.where_has(
            "from_country", lambda query: query.where("name", "USA")
        ).to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `inbound_shipments` WHERE EXISTS (SELECT * FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id` AND `countries`.`name` = 'USA')""",
        )

    def test_or_where_has(self):
        sql = (
            InboundShipment.where("name", "Joe")
            .or_where_has("from_country", lambda query: query.where("name", "USA"))
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `inbound_shipments` WHERE `inbound_shipments`.`name` = 'Joe' OR EXISTS (SELECT * FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id` AND `countries`.`name` = 'USA')""",
        )

    def test_doesnt_have(self):
        sql = InboundShipment.doesnt_have("from_country").to_sql()

        self.assertEqual(
            sql,
            """SELECT * FROM `inbound_shipments` WHERE NOT EXISTS (SELECT * FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id`)""",
        )

    def test_or_where_doesnt_have(self):
        sql = (
            InboundShipment.where("name", "Joe")
            .or_where_doesnt_have(
                "from_country", lambda query: query.where("name", "USA")
            )
            .to_sql()
        )

        self.assertEqual(
            sql,
            """SELECT * FROM `inbound_shipments` WHERE `inbound_shipments`.`name` = 'Joe' OR NOT EXISTS (SELECT * FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id` AND `countries`.`name` = 'USA')""",
        )

    def test_has_one_through_with_count(self):
        sql = InboundShipment.with_count("from_country").to_sql()

        self.assertEqual(
            sql,
            """SELECT `inbound_shipments`.*, (SELECT COUNT(*) AS m_count_reserved FROM `countries` INNER JOIN `ports` ON `ports`.`country_id` = `countries`.`country_id` WHERE `ports`.`port_id` = `inbound_shipments`.`from_port_id`) AS from_country_count FROM `inbound_shipments`""",
        )
