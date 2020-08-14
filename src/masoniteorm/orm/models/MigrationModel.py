from .Model import Model


class MigrationModel(Model):

    __table__ = "migrations"
    __fillable__ = ["migration", "batch"]
