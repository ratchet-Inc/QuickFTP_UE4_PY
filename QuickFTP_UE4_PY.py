import datetime
import ArgsParser
import DB_Interface
from SocketController import SocketController

class Container(object):
    def __init__(self, *args, **kwargs):
        self.fPtr = None
        self.state: int = 0
        self.sql: DB_Interface.DB_Interface = None
        return super().__init__(*args, **kwargs)

    def InitComps(self, args: dict)-> int:
        self.rootDir = args['storageDir']
        self.sql = DB_Interface.DB_Interface(args['host'], args['username'], args['passw'], args['dbName'])
        val = self.sql.ConnectToDB()
        if val != 0:
            return val
        self.sock = SocketController(host = args['listenHost'], port = args['listenPort'])
        val = self.sock.InitSocket_Server()
        if val != 0:
            return val
        return 0

    def ConnectToClient():
        try:
            (conn, addr) = self.sock.Listen()
            self.clientConn = conn
            self.clientAddr = addr
            pass
        except:
            return 1
        return 0

    def CheckUploads(self):
        query = 'SELECT * FROM RenderStreamUploads WHERE rendered = false LIMIT = 1;'
        res = self.sql.SendQuery(query)
        if res != 0:
            return 1, res
        res = self.sql.ReadQuery()
        return 0, res

    def UpdateRenderedInfo(self, pkey):
        query = 'UPDATE RenderStreamUploads SET renderedTime = {time} , rendered = true WHERE pKey = {key};'
        data ={"time": datetime.datetime.now().timestamp(), "key": pkey}
        r = self.sql.SendQuery(query, data)
        if r != 0:
            return 1, r
        return 0, self.sql.ReadQuery()

    def Tick(self, delta: float)-> int:
        return 0

    def CloseComps(self):
        self.sock.Close()
        self.sql.Close()
        pass
    pass

def mainFunction():
    args = ArgsParser.ParseArguments()
    obj = Container()
    obj.InitComps(args)
    obj.CloseComps()
    print("ran")
    return 0

if "__main__" == __name__:
    mainFunction()
    pass
