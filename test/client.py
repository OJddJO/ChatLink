import socket

class Client:
    def __init__(self, username, host, port):
        self._username = username
        self._host = host
        self._port = port
        self._BUFFER = 1024
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.connect((self._host, self._port))
        self._client.send(self._username.encode("utf-8"))
    
    
