import socket
import threading
import os
import json
from datetime import datetime

class Server:
    def __init__(self):
        # initialize server files
        if not os.path.exists("./serverData"):
            os.mkdir("./serverData")
            json.dump({}, open("./serverData/users.json", "w"))
            json.dump({}, open("./serverData/groups.json", "w"))
            json.dump({}, open("./serverData/privateMessages.json", "w"))

        self._HOST = "127.0.0.1"
        self._PORT = 5000
        self._BUFFER = 1024
        self._clients = []
        self._addresses = []
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((self._HOST, self._PORT))
        self._server.listen()
        self._running = True
        print(f"Server is listening on {self._HOST}:{self._PORT}")

    def start(self):
        while self._running:
            conn, addr = self._server.accept()
            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()
        self._server.close()

    def handleClient(self, conn, addr):
        print(f"New connection from {addr}")
        self._clients.append(conn)
        self._addresses.append(addr)
        username = conn.recv(self._BUFFER).decode("utf-8")
        conn.send("Connected to the server".encode("utf-8"))
        print(f"Client {username} at {addr}: Connected")

        while self._running:
            try:
                data = conn.recv(self._BUFFER).decode("utf-8")
                if not data:
                    print(f"Client {username} at {addr}: Disconnected")
                    break
                data = eval(data)
                response = self.manageData(data)
                conn.send(str(response).encode("utf-8"))
            except Exception as e:
                print(f"Client {username} at {addr} lost connection: {e}")
                break

        conn.close()
        self._clients.remove(conn)
        self._addresses.remove(addr)

    def manageData(self, data):
        try:
            if data["group"] == "private":
                message = data["msg"]["message"]
                sender = data["msg"]["sender"]
                receiver = data["msg"]["channel"]
                channel = ",".join(sorted([sender, receiver]))
                privateMessages = json.load(open("./serverData/privateMessages.json", "r"))
                if data["msg"]["message"] != "":
                    data = {
                        "sender": sender,
                        "channel": receiver,
                        "message": message,
                        "time": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    if channel not in privateMessages:
                        privateMessages[channel] = []
                    privateMessages[channel].append(data)
                    if len(privateMessages[channel]) > 100:
                        privateMessages[channel].pop(0)
                    json.dump(privateMessages, open("./serverData/privateMessages.json", "w"))
                return channel, privateMessages[channel]
            else:
                message = data["msg"]["message"]
                sender = data["msg"]["sender"]
                group = data["msg"]["group"]
                channel = data["msg"]["channel"]
                groups = json.load(open("./serverData/groups.json", "r"))
                if data["msg"]["message"] != "":
                    data = {
                        "sender": sender,
                        "message": message,
                        "time": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    if group not in groups:
                        groups[group] = {}
                    if channel not in groups[group]:
                        groups[group][channel] = []
                    groups[group][channel].append(data)
                    if len(groups[group][channel]) > 100:
                        groups[group][channel].pop(0)
                    json.dump(groups, open("./serverData/groups.json", "w"))
                return channel, groups[group][channel]
        except Exception as e:
            pass


if __name__ == "__main__":
    server = Server()
    server.start()