from src.masoniteorm.models import Model

class User(Model):
    __table__ = "tbl_users"
    __primary_key__ = "user_id"

    @property
    def company(self):
        return self.has_one(Company, "company_id", "company_id")

class CreditCard(Model):
    __table__ = "company_credit_cards"
    __primary_key__ = "credit_card_id"

    @property
    def company(self):
        return self.has_one(Company, "company_id", "company_id")

class Company(Model):
    __table__ = "tbl_companies"
    __primary_key__ = "company_id"


    @property
    def cards(self):
        return self.has_many(CreditCard, "company_id", "company_id")

# Usage has one
user = User.find(667)

# fetches record on related company record
for card in user.company.cards:
    print(card.company.company_name)

# user.company() part returns a query builder so we can fetch related queries on the fly
print(user.company().limit(1).to_sql())  # Output: select * from tbl_companies where tbl_companies.company_id = 373849