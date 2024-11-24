from src.masoniteorm.models import Model

class User(Model):
    __table__ = "tbl_users"
    __primary_key__ = "user_id"

    @property
    def company(self):
        related = Company()

        related.owner = self
        return HasOne(related, "company_id", "company_id")(self)


class Company(Model):
    __table__ = "tbl_companies"
    __primary_key__ = "company_id"

    def __call__(self):
        foreign_key_value = self.__dict__['related'].owner.__attributes__.get(self.__dict__['related'].foreign_key)
        builder = self.builder.where(self.__dict__['related'].local_key, foreign_key_value)
        return builder

class BaseRelationship:
    def init(self, model_class, local_key=None, foreign_key=None):
        self.model_class = model_class
        self.local_key = local_key
        self.foreign_key = foreign_key

    def __call__(self, owner):
        """Create and return the relationship query."""
        # self.set_keys(owner)
        related_model = self.model_class()
        return self.apply_query(related_model.builder, owner)

class HasOne(BaseRelationship):
    """Belongs To Relationship Class."""

    def __init__(self, model_class, foreign_key=None, local_key=None):
        self.model_class = model_class
        self.foreign_key = foreign_key
        self.local_key = local_key

    def __call__(self, owner):
        """Fetch the related record when invoked."""
        related_model = self.model_class
        # print("related model", related_model)
        related_model.owner = self
        foreign_key_value = owner.__attributes__.get(self.foreign_key)
        if not foreign_key_value:
            return None
        builder = related_model.builder.where(self.local_key, foreign_key_value)
        result = builder.first()
        self.owner = owner
        result.__dict__['related'] = self
        return result


# Usage has one
user = User.find(667)

# fetches record on related company record
print(user.company.company_name)  # Output: Company name

# user.company() part returns a query builder so we can fetch related queries on the fly
print(user.company().to_sql())  # Output: select * from tbl_companies where tbl_companies.company_id = 373849