import SocketController

class QuickFTP(object):
    """
    description:-   A simple file transfer class to send binary files over a socket.
    """
    def __init__(self, dir: str, socket: SocketController.SocketController):
        self.filesDirectory = dir
        self.curFile = None
        self.sock = socket
        pass
pass


