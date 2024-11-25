"""Test the default global scopes available in ORM."""
import unittest
import uuid
import pendulum

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import (
    SoftDeletesMixin,
    TimeStampsScope,
    TimeStampsMixin,
    UUIDPrimaryKeyScope,
    UUIDPrimaryKeyMixin,
)


class MockBuilder:
    def __init__(self, model):
        self._model = model()
        self._creates = {}
        self._updates = {}


class UserWithUUID(Model, UUIDPrimaryKeyMixin):
    __dry__ = True


class UserWithTimeStamps(Model, TimeStampsMixin):
    __dry__ = True


class UserWithCustomTimeStamps(Model, TimeStampsMixin):
    __dry__ = True
    date_updated_at = "updated_ts"
    date_created_at = "created_ts"


class UserSoft(Model, SoftDeletesMixin):
    __dry__ = True


class TestUUIDPrimaryKeyScope(unittest.TestCase):
    def setUp(self):
        self.builder = MockBuilder(UserWithUUID)
        self.scope = UUIDPrimaryKeyScope()
        # reset User attributes before each test
        UserWithUUID.__primary_key__ = "id"
        flags = {
            "__uuid_version__",
            "__uuid_namespace__",
            "__uuid_name__",
            "__uuid_bytes__",
        }
        for flag in flags:
            if hasattr(UserWithUUID, flag):
                delattr(UserWithUUID, flag)

    def test_default_to_uuid4(self):
        self.scope.set_uuid_create(self.builder)
        uuid_value = uuid.UUID(self.builder._creates["id"])
        self.assertEqual(4, uuid_value.version)

    def test_can_set_uuid_version(self):
        # required for uuid 3 and 5
        UserWithUUID.__uuid_namespace__ = uuid.NAMESPACE_DNS
        UserWithUUID.__uuid_name__ = "domain.com"
        for version in [1, 3, 4, 5]:
            UserWithUUID.__uuid_version__ = version
            self.scope.set_uuid_create(self.builder)
            uuid_value = uuid.UUID(self.builder._creates["id"])
            self.assertEqual(version, uuid_value.version)
            del self.builder._creates["id"]

    def test_default_to_uuid_str(self):
        # Generates UUIDs as strings by default
        self.scope.set_uuid_create(self.builder)
        self.assertIsInstance(self.builder._creates["id"], str)

    def test_can_set_uuid_bytes(self):
        # Generates UUIDs in bytes instead of strings
        UserWithUUID.__uuid_bytes__ = True
        self.scope.set_uuid_create(self.builder)
        self.assertIsInstance(self.builder._creates["id"], bytes)

    def test_works_with_custom_pk_column(self):
        UserWithUUID.__primary_key__ = "ref"
        self.scope.set_uuid_create(self.builder)
        self.assertIn("ref", self.builder._creates)


class TestSoftDeletesScope(unittest.TestCase):
    def test_soft_deletes_changes_delete_to_update(self):
        UserSoft.__timestamps__ = False
        user = UserSoft.hydrate({"id": 1})
        sql = user.delete(query=True).to_sql()
        self.assertTrue(sql.startswith("UPDATE"))


class TestTimeStampsScope(unittest.TestCase):
    def setUp(self):
        self.builder = MockBuilder(UserWithTimeStamps)
        self.scope = TimeStampsScope()
        try:
            del UserWithTimeStamps.__timestamps__
        except:
            pass

    def test_updated_and_created_dates_are_set_when_create(self):
        self.scope.set_timestamp_create(self.builder)
        self.assertIn("created_at", self.builder._creates)
        self.assertIn("updated_at", self.builder._creates)
        created_at = pendulum.parse(self.builder._creates["created_at"])
        updated_at = pendulum.parse(self.builder._creates["updated_at"])
        self.assertIsInstance(created_at, pendulum.DateTime)
        self.assertIsInstance(updated_at, pendulum.DateTime)

    def test_timestamps_can_be_disabled(self):
        UserWithTimeStamps.__timestamps__ = False
        self.scope.set_timestamp_create(self.builder)
        self.assertNotIn("created_at", self.builder._creates)
        self.assertNotIn("updated_at", self.builder._creates)

    def test_uses_custom_timestamp_columns_on_create(self):
        self.builder = MockBuilder(UserWithCustomTimeStamps)
        self.scope.set_timestamp_create(self.builder)
        created_column = UserWithCustomTimeStamps.date_created_at
        updated_column = UserWithCustomTimeStamps.date_updated_at
        self.assertNotIn("created_at", self.builder._creates)
        self.assertNotIn("updated_at", self.builder._creates)
        self.assertIn(created_column, self.builder._creates)
        self.assertIn(updated_column, self.builder._creates)
        self.assertIsInstance(
            pendulum.parse(self.builder._creates[created_column]), pendulum.DateTime
        )
        self.assertIsInstance(
            pendulum.parse(self.builder._creates[updated_column]), pendulum.DateTime
        )

    def test_uses_custom_updated_column_on_update(self):
        user = UserWithCustomTimeStamps.hydrate({"id": 1})
        sql = user.update({"id": 2}).to_sql()
        self.assertTrue(UserWithCustomTimeStamps.date_updated_at in sql)
