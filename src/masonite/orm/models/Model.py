from ..connections.ConnectionFactory import ConnectionFactory


class Model:

    __fillable__ = []
    __guarded__ = ["*"]
    __table__ = "users"
    __connection__ = "default"
    __resolved_connection__ = None

    _booted = False

    def boot(self):
        self.__resolved_connection__ = ConnectionFactory.make(self.__connection__)

    def first(self):
        pass

    def find(self):
        pass

    def first_or_new(self):
        pass

    def first_or_create(self):
        pass

    def where(self):
        pass

    def limit(self):
        pass

    def select(self):
        pass

    def hydrate(self):
        pass

    def fill(self):
        pass

    def create(self):
        pass

    def delete(self):
        pass

    def get(self):
        pass

    def find_or_fail(self):
        pass

    def update_or_create(self):
        pass

    def touch(self):
        pass
