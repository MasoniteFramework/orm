from .Model import Model


class MigrationModel(Model):

    __table__ = "migrations"
    __fillable__ = ["migration", "batch"]
    __timestamps__ = None

    __primary_key__ = "migration_id"
