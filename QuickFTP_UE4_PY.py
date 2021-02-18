import datetime
import ArgsParser
import DB_Interface
import SocketController
import time
import signal
import errno

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

    def ConnectToClient(self):
        try:
            (conn, addr) = self.sock.Listen()
            self.clientConn = conn
            self.clientAddr = addr
            pass
        except:
            return 1
        return 0

    def CheckUploads(self):
        query = 'SELECT * FROM RenderStreamUploads WHERE rendered = false LIMIT 1;'
        res = self.sql.SendQuery(query)
        if res != 0:
            return 1, res
        res = self.sql.ReadQuery()
        return 0, res

    def UpdateRenderedInfo(self, pkey: int, renderResult: int)-> int:
        # renderResult value: 0 for not yet rendered, 1 for success, 2 for failure
        query = 'UPDATE RenderStreamUploads SET renderedTime = {time} , rendered = {ren} WHERE pKey = {key};'
        data = {"time": datetime.datetime.now().timestamp(), "key": pkey, "ren": renderResult}
        r = self.sql.SendQuery(query, data)
        if r != 0:
            return 1, r
        return 0, self.sql.ReadQuery()

    def FetchFile(self):
        if self.fileData == None:
            print("File name is invalid.")
            pass
        if self.state == 1 and self.fileData != None:
            fn = self.rootDir + self.fileData['filename']
            try: 
                file = open(fn, "rb")
                self.fileData['rawBytes'] = file.read()
                file.close()
                self.fileData['bytesLen'] = len(self.fileData['rawBytes'])
                self.state = 2
            except OSError:
                print("*Error: file[%s] not found." % fn)
                pass
            pass
        return 0

    def Request_GetDataInfo(self):
        if self.fileData == None:
            return 1
        fileSize = 0
        if self.fileData.get('bytesLen') != None:
            fileSize = self.fileData['bytesLen']
            self.state = 4
            pass
        sent = self.sock.SendData(self.clientConn, str(fileSize))
        dataLen = len(bytes(str(fileSize).encode('utf-8'))) + 1
        if sent != dataLen:
            print("Bytes sent is invalid: %d != %d." % (sent, dataLen))
            return 1
        return 0

    def Request_SendFileBytes(self):
        if self.fileData == None or self.fileData['rawBytes'] == None:
            return 1
        sent = self.sock.SendBytes(self.clientConn, self.fileData['rawBytes'])
        dataLen = len(self.fileData['rawBytes']) + 1
        if sent < dataLen:
            print("Bytes sent is invalid: %d < %d." % (sent, dataLen))
            return 1
        return 0

    def Request_DenyFile(self):
        self.fileDenied = True
        return self.UpdateRenderedInfo(self.FetchFile['pkey'], 2)

    def ProcessClientRequest(self, req):
        CONST_GET_INFO_REQ = 'PL\0'
        CONST_GET_DATA_REQ = 'DATA\0'
        CONST_DENY_REQ = 'BAD\0'
        func = None
        if self.state == 4:
            if req == self.fileData['bytesLen']:
                self.state = 2
                return self.UpdateRenderedInfo(self.FetchFile['pkey'], 1)
            pass
        # checking at processing procedure we should take
        if req == CONST_GET_INFO_REQ:
            func = self.Request_GetDataInfo
        elif req == CONST_GET_DATA_REQ:
            func = self.Request_SendFileBytes
        elif req == CONST_DENY_REQ:
            func = self.Request_DenyFile
        else:
             print("*Error: client request unknown: '%s'.\n" % req)
             pass
        if func == None:
            return 1
        return func()

    def Tick(self, delta: float)-> int:
        reVal = 0
        if self.fileDenied == True:
            self.fileDenied = False
            self.state = 3
            self.fileData['bytesLen'] = None
            pass
        # database instructions
        if self.state == 3 or self.fileData == None:
            reVal, res = self.CheckUploads()
            if reVal == 0 and len(res) > 0:
                self.fileData = {}
                self.fileData['filename'] = res[0][1]
                self.fileData['pkey'] = res[0][0]
                self.state = 1
                pass
            pass
        # socket instructions
        self.FetchFile()
        try:
            data = self.sock.RecvData(self.clientConn, "utf-16")
            print("recieved: %s" % data)
            reVal = self.ProcessClientRequest(data.strip().rstrip())
        except SocketController.socket.error as e:
            err = e.args[0]
            if err != errno.EAGAIN and err != errno.EWOULDBLOCK:
                print("*Error: A socket error occured.")
                return 1
            pass
        return reVal

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
    IS_RUNNING: bool = True
    def IntervalSignalHandler(signum, frame):
        print("Signal received: %s | %s." % (signum, frame))
        IS_RUNNING = False
        pass
    signal.signal(signal.SIGINT, IntervalSignalHandler)
    signal.signal(signal.SIGTERM, IntervalSignalHandler)
    reval = 0
    args = ArgsParser.ParseArguments()
    obj = Container()
    obj.InitComps(args)
    print("waiting for client.")
    reVal = obj.ConnectToClient()
    if reVal != 0:
        print("unexpected error: %d" % reVal)
        obj.CloseComps()
        return reVal
    print("client connected.")
    loopTime = 0.0667       # tick at approximately 15 times a second.
    lastInterval = time.time()
    while IS_RUNNING:
        reVal = obj.Tick(time.time() - lastInterval)
        if reVal != 0:
            break
        # dynamic sleep to ensure we operate at the desired rate
        t = time.time()
        sleepTime = t - lastInterval
        if sleepTime > loopTime:
            sleepTime = loopTime
            pass
        lastInterval = t
        time.sleep(sleepTime)
        pass
    obj.CloseComps()
    return reVal

if "__main__" == __name__:
    try:
        mainFunction()
    except KeyboardInterrupt:
        print("process ended.")
        pass
    pass
