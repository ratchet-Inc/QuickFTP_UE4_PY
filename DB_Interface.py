import mysql.connector
from mysql.connector import errorcode

class DB_Interface(object):
    """
    description:-   a simple database wrapper to create for abstraction.
    """
    def __init__(self, hostName: str, loginUser: str, loginPasscode: str, dbName: str):
        self.host = hostName
        self.loginName = loginUser
        self.db = dbName
        self.pw = loginPasscode
        self.cursor = None
        self.connection = None
        pass
    def ConnectToDB(self):
        try:
            self.connection = mysql.connector.connect(user = self.loginName, passwd = self.pw, host = self.host, database = self.db)
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Bad login credentials!")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("The requested database does not exist!")
            else:
                print("Unknown error: %s." % err)
                pass
            return 1
        return 0
    def Close(self):
        if self.connection != None:
            self.cursor.close()
            self.connection.close()
            self.connection = None
            pass
        pass
    def SendQuery(self, query: str, queryData: dict = None)->int:
        if len(query) > 0:
            q = query
            if queryData != None:
                q = q.format(**queryData)
                pass
            self.cursor.execute(q)
            return 0
        return 1
    def ReadQuery(self)-> tuple:
        return self.cursor.fetchall()
    def CommitDB(self):
        self.connection.commit()
        return 0
    pass