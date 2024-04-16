import socket
import threading
import os
import json

class Server:
    def __init__(self):
        # initialize server files
        if os.path.exists("./data") == False:
            os.mkdir("./data")
            json.dump({}, open("./data/users.json", "w"))
            json.dump({}, open("./data/groups.json", "w"))
            json.dump({}, open("./data/privateMessages.json", "w"))

        self._HOST = input("Enter the server IP address: ")
        self._PORT = int(input("Enter the server port: "))
        self._BUFFER = 1024
        self._clients = []
        self._addresses = []
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((self._HOST, self._PORT))
        self._server.listen()
        self._running = True
        print(f"Server is listening on {self._HOST}:{self._PORT}")

    def handleConsoleInput(self):
        while self._running:
            cmd = input()
            match cmd:
                case "exit":
                    self._running = False
                    print("Server shutting down...")
                    for conn in self._clients:
                        conn.close()
                    break

    def start(self):
        consoleThread = threading.Thread(target=self.handleConsoleInput)
        consoleThread.start()
        self.acceptConn()

    def acceptConn(self):
        while self._running:
            conn, addr = self._server.accept()
            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()
        self._server.close()

    def initClient(self, username):
        users = json.load(open("./data/users.json", "r"))
        if username not in users:
            users[username] = {
                "friends": [],
                "groups": []
            }
            json.dump(users, open("./data/users.json", "w"))
        data = users[username]
        return data

    def handleClient(self, conn, addr):
        print(f"New connection from {addr}")
        self._clients.append(conn)
        self._addresses.append(addr)

        username = conn.recv(self._BUFFER).decode("utf-8")
        print(f"Client {username} at {addr}: Connected")

        while self._running:
            try:
                data = conn.recv(self._BUFFER).decode("utf-8")
                if not data:
                    print(f"Client {username} at {addr}: Disconnected")
                    break
                conn.sendall(data)
            except Exception as e:
                print(f"Client {username} at {addr} lost connection: {e}")
                break

        conn.close()
        self._clients.remove(conn)
        self._addresses.remove(addr)


if __name__ == "__main__":
    server = Server()
    server.start()