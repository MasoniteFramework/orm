"""StoreTableSeeder Seeder."""

from src.masoniteorm.models import Model
from src.masoniteorm.seeds import Seeder


class Store(Model):
    __connection__ = "dev"
    __table__ = "stores"


class Product(Model):
    __connection__ = "dev"
    __table__ = "products"


class ProductStore(Model):
    __connection__ = "dev"
    __table__ = "product_store"
    __timestamps__ = False


class StoreTableSeeder(Seeder):
    def run(self):
        """
        Seed stores, products, and the product_store pivot table.

        test_belongs_to_many hydrates Store(id=2) and asserts:
          - store.products.count() == 3
          - first product id=4, name='Handgun'
          - product created_at/updated_at == '2020-01-01T00:00:00+00:00'

        test_belongs_to_eager_many calls Store.with_('products').first() (store id=1)
        and asserts store.products.count() == 3.

        Layout:
          Store 1 (Walmart) → products 1, 2, 3  (Pants, Shirt, Flag)
          Store 2 (Target)  → products 4, 5, 6  (Handgun, Rifle, Machine Gun)
        """
        Store.bulk_create(
            [
                {
                    "name": "Walmart",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "name": "Target",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
            ]
        )

        Product.bulk_create(
            [
                {
                    "name": "Pants",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "name": "Shirt",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "name": "Flag",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "name": "Handgun",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "name": "Rifle",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "name": "Machine Gun",
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
            ]
        )

        # Pivot rows — store 1 gets products 1-3, store 2 gets products 4-6.
        ProductStore.bulk_create(
            [
                {
                    "product_id": 1,
                    "store_id": 1,
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "product_id": 2,
                    "store_id": 1,
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "product_id": 3,
                    "store_id": 1,
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "product_id": 4,
                    "store_id": 2,
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "product_id": 5,
                    "store_id": 2,
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
                {
                    "product_id": 6,
                    "store_id": 2,
                    "created_at": "2020-01-01",
                    "updated_at": "2020-01-01",
                },
            ]
        )
