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
    def SendData(self, conn:socket, msg: str)->int:
        return conn.send(str(msg+'\0').encode("utf-8"))
    def RecvData(self, conn: socket) -> str:
        return conn.recv(self.buffLen).decode()
    def Close(self):
        self.ssocket.close()
        pass
    pass
