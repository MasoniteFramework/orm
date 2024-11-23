class Database:
    """
    Simulate a database query. Replace this with actual database calls.
    """
    @staticmethod
    def get(table, conditions):
        # Dummy data for demonstration
        data = {
            "companies": [{"company_id": 1, "name": "Acme Corp"}],
            "users": [{"user_id": 1, "company_id": 1, "name": "John Doe"}],
        }
        return data['companies'][0]


class HasOne:
    def __init__(self, parent, related_model, foreign_key, local_key):
        self.parent = parent
        self.related_model = related_model
        self.foreign_key = foreign_key
        self.local_key = local_key
        self._related_instance = None

    def get(self):
        """
        Perform the database query to fetch the related model.
        """
        if self._related_instance is None:
            related_data = Database.get(
                self.related_model.table_name(),
                {self.foreign_key: getattr(self.parent, self.local_key)}
            )
            if related_data:
                self._related_instance = self.related_model(**related_data)
        return self._related_instance

    def __call__(self):
        """
        Allow the relationship instance to be callable.
        """
        return self


class RelationshipProperty:
    """
    A wrapper for dual behavior: as a property and as a callable returning the relationship instance.
    """
    def __init__(self, relationship):
        self.relationship = relationship

    def __getattr__(self, name):
        """
        Delegate attribute access to the related model instance.
        """
        print("Delegating attribute access to the related model instance")
        related_instance = self.relationship.get()
        if related_instance:
            return getattr(related_instance, name)
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")

    def __call__(self):
        """
        Make the relationship callable to return the relationship instance.
        """
        return self.relationship

    def __repr__(self):
        return repr(self.relationship.get())

    


class Model:
    """
    Base model class to share common functionality.
    """
    @classmethod
    def table_name(cls):
        return cls.__name__.lower() + "s"  # Example: User -> users

    def has_one(self, related_model, foreign_key=None, local_key="id"):
        return RelationshipProperty(HasOne(self, related_model, foreign_key, local_key))


class Company(Model):
    def __init__(self, company_id, name):
        self.company_id = company_id
        self.name = name

    def welcome(self):
        return f"Welcome to {self.name}"

class User(Model):
    def __init__(self, user_id, company_id, name):
        self.user_id = user_id
        self.company_id = company_id
        self.name = name

    @property
    def company(self):
        """
        Return a RelationshipProperty wrapper for dual behavior.
        """
        return self.has_one(Company, "company_id", "company_id")


# Usage
user = User(user_id=1, company_id=1, name="John Doe")

# Access the related company instance as a property
related_company = user.company
print("property", related_company)  # Output: Acme Corp
print("property", related_company.name, related_company.name=="Acme Corp")  # Output: Acme Corp

# Call the relationship instance to get the related company
related_company_callable = user.company()
print("callable", isinstance(related_company_callable, HasOne))  # Output: True
