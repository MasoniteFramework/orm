from .mysql_grammer import MySQLGrammer
from .mssql_grammer import MSSQLGrammer

class GrammerFactory:

    grammers = {
        'mysql': MySQLGrammer,
        'mssql': MSSQLGrammer,
    }

    @staticmethod
    def make(key):
        grammer = GrammerFactory.grammers.get(key)
        if grammer:
            return grammer