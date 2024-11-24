from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.models import Model
from src.masoniteorm.models.relationships import HasOne


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


# Usage
# user = User(user_id=1, company_id=1, name="John Doe")
user = User.find(667)

# Access the related company instance as a property
related_company = user.company
print("property name", related_company.company_name)  # Output: Acme Corp
# print("property 2", related_company.company_name, related_company.company_name=="Acme Corp")  # Output: Acme Corp

# # Call the relationship instance to get the related company
# related_company_callable = user.company().get()
# cards = user.company.cards
company = Company.find(373849)

print(company.cards)
# for card in company.cards:
#     print(card)
# print(company.cards().where("is_default", 1).get())
# print("callable", isinstance(user.company(), HasOne))  # Output: True

