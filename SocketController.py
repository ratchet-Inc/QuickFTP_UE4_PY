import socket

class SocketController(object):
    """ A simple socket abstraction class to remove complexity elsewhere """
    def __init__(self, host, port, bufferLen = 2048):
        self.host = host
        self.port = port
        self.buffLen = bufferLen
        pass
    def InitSocket_Server(self, IsBlocking = True):
        try:
            self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if not IsBlocking:
                self.ssocket.setblocking(False)
                pass
            self.ssocket.bind((self.host, self.port))
            pass
        except:
            return 1
        return 0
    def Listen(self):
        self.ssocket.listen()
        return self.ssocket.accept()
    def SendData(self, conn:socket, msg: str, encoding: str = "utf-8")->int:
        return conn.send(str(msg+'\0').encode(encoding))
    def SendBytes(self, conn: socket, msg: bytes)->int:
        return conn.send(msg + bytes(b'\0'))
    def RecvData(self, conn: socket, encoding: str = "utf-8") -> str:
        return conn.recv(self.buffLen).decode(encoding)
    def Close(self):
        self.ssocket.close()
        pass
    pass
