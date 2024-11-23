import unittest
from src.masoniteorm.models import Model

class CreditCard(Model):
    __table__ = "company_credit_cards"
    __primary_key__ = "credit_card_id"


class Company(Model):
    __table__ = "tbl_companies"
    __primary_key__ = "company_id"

    @property
    def cards(self):
        """
        Return a RelationshipProperty wrapper for dual behavior.
        """
        return self.has_many(CreditCard, "company_id", "company_id")

class User(Model):
    __table__ = "tbl_users"
    __primary_key__ = "user_id"

    @property
    def company(self):
        """
        Return a RelationshipProperty wrapper for dual behavior.
        """
        return self.has_one(Company, "company_id", "company_id")


class PlaygroundTest(unittest.TestCase):
    def test_has_one_can_access_related_model_attribute(self):
        user = User.find(667)

        # Access the related company instance as a property
        related_company = user.company
        self.assertEqual(related_company.company_name, "ROTHCO ACCOUNT")

    def test_has_one_can_build_off_query_builder(self):
        user = User.find(667)

        # Access the related company instance as a property
        related_company = user.company
        # self.assertEqual(related_company.company_name, "ROTHCO ACCOUNT")
        self.assertEqual(user.company().to_sql(), "SELECT * FROM `tbl_companies` WHERE `tbl_companies`.`company_id` = '373849'")