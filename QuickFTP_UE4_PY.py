import datetime
import ArgsParser
import DB_Interface
import SocketController

class Container(object):
    def __init__(self, *args, **kwargs):
        self.fPtr = None
        self.sock: SocketController.SocketController = None
        self.clientConn: SocketController.socket = None
        self.clientAddr: str = None
        self.fileData: dict = None
        self.fileDenied: bool = False
        self.state: int = 0
        self.sql: DB_Interface.DB_Interface = None
        return super().__init__(*args, **kwargs)

    def InitComps(self, args: dict)-> int:
        self.rootDir = args['storageDir']
        self.sql = DB_Interface.DB_Interface(args['host'], args['username'], args['passw'], args['dbName'])
        val = self.sql.ConnectToDB()
        if val != 0:
            return val
        self.sock = SocketController.SocketController(host = args['listenHost'], port = args['listenPort'])
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

    def Request_GetDataInfo(self):
        if not self.fileData:
            return 1
        sent = self.sock.SendData(self.clientConn, str(self.fileData['bytesLen']))
        dataLen = len(bytes(str(self.fileData['bytesLen']+1)))
        if sent != dataLen:
            print("Bytes sent is invalid: %d != %d." % (sent, dataLen))
            return 1
        return 0

    def Request_SendFileBytes(self):
        if self.fileData == None:
            return 1
        sent = self.sock.SendData(self.clientConn, str(self.fileData['rawBytes']))
        dataLen = len(bytes(str(self.fileData['rawBytes']+1)))
        if sent != dataLen:
            print("Bytes sent is invalid: %d != %d." % (sent, dataLen))
            return 1
        return 0

    def Request_DenyFile(self):
        self.fileDenied = True
        return 0

    def ProcessClientRequest(self, req):
        CONST_GET_INFO_REQ = 'PL'
        CONST_GET_DATA_REQ = 'DATA'
        CONST_DENY_REQ = 'BAD'
        func = None
        if req == CONST_GET_INFO_REQ:
            func = self.Request_GetDataInfo
        elif req == CONST_GET_DATA_REQ:
            func = self.Request_SendFileBytes
        elif req == CONST_DENY_REQ:
             func = self.Request_SendFileBytes
        else:
             print("*Error: client requesrt unknown: '%s'.\n" % req)
             pass
        if func == None:
            return 1
        return func()

    def Tick(self, delta: float)-> int:
        return 0

    def CloseComps(self):
        if self.sock != None:
            self.sock.Close()
            pass
        if self.sql != None:
            self.sql.Close()
            pass
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
