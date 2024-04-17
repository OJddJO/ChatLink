import socket
import threading
import os
import json

class Client:
    def __init__(self, host, port):
        self._username = input("Enter your username: ")
        self._host = host
        self._port = port
        self._BUFFER = 1024
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.path = f"./{self._username}data"
        if not os.path.exists(self.path): # Initialize user data
            os.mkdir(self.path)
            json.dump({}, open(f"{self.path}/privateMessages.json", "w"))
            json.dump({}, open(f"{self.path}/groups.json", "w"))
            json.dump({}, open(f"{self.path}/settings.json", "w"))

        self.privateMessages = json.load(open(f"{self.path}/privateMessages.json"))
        self.groups = json.load(open(f"{self.path}/groups.json"))
        self.settings = json.load(open(f"{self.path}/settings.json"))
        self.currentGroup = "PkPas"
        self.currentChannel = "General"
        self.msg = {
            "sender": self._username,
            "group": self.currentGroup,
            "channel": self.currentChannel,
            "message": ""
        }

    def connect(self):
        self._client.connect((self._host, self._port))
        self._client.send(self._username.encode("utf-8"))
        print(self._client.recv(self._BUFFER).decode("utf-8"))
    
    def handleInput(self):
        while True:
            message = input()
            if message == "exit":
                self._client.close()
                break
            self.msg["message"] = message

    def send(self):
        while True:
            data = str({
                "msg": self.msg,
                "username": self._username,
                "group": self.currentGroup,
                "channel": self.currentChannel
            })
            self._client.send(data.encode("utf-8"))
            self.msg["message"] = ""
            self.manageData(self._client.recv(self._BUFFER).decode("utf-8"))

    def renderMessages(self):
        if self.currentGroup == "private":
            channel = ",".join(sorted([self._username, self.currentChannel]))
            if channel in self.privateMessages:
                for message in self.privateMessages[channel]:
                    print(f"{message['sender']} {message['time']}: {message['message']}")
        if self.currentGroup in self.groups:
            if self.currentChannel in self.groups[self.currentGroup]:
                for message in self.groups[self.currentGroup][self.currentChannel]:
                    print(f"{self.currentGroup}>{self.currentChannel} {message['sender']} {message['time']}: {message['message']}")

    def manageData(self, data):
        try:
            data = eval(data)
            if self.currentGroup == "private":
                if data[0] not in self.privateMessages:
                    self.privateMessages[data[0]] = data[1]
                    for element in data[1]:
                        print(f"{element['sender']} {element['time']}: {element['message']}")
                    self.saveData()
                else:
                    changes = False
                    for element in data[1]:
                        if element not in self.privateMessages[data[0]]:
                            changes = True
                            self.privateMessages[data[0]].append(element)
                            if len(self.privateMessages[data[0]]) > 100:
                                self.privateMessages[data[0]].pop(0)
                            print(f"{element['sender']} {element['time']}: {element['message']}")
                    if changes:
                        self.saveData()
            else:
                if self.currentGroup not in self.groups:
                    self.groups[self.currentGroup] = {}
                if data[0] not in self.groups[self.currentGroup]:
                    self.groups[self.currentGroup][data[0]] = data[1]
                    for element in data[1]:
                        print(f"{self.currentGroup}>{self.currentChannel} {element['sender']} {element['time']}: {element['message']}")
                    self.saveData()
                else:
                    changes = False
                    for element in data[1]:
                        if element not in self.groups[self.currentGroup][data[0]]:
                            changes = True
                            self.groups[self.currentGroup][data[0]].append(element)
                            if len(self.groups[self.currentGroup][data[0]]) > 100:
                                self.groups[self.currentGroup][data[0]].pop(0)
                            print(f"{self.currentGroup}>{self.currentChannel} {element['sender']} {element['time']}: {element['message']}")
                    if changes:
                        self.saveData()
        except Exception as e:
            pass

    def saveData(self):
        json.dump(self.privateMessages, open(f"{self.path}/privateMessages.json", "w"))
        json.dump(self.groups, open(f"{self.path}/groups.json", "w"))
        json.dump(self.settings, open(f"{self.path}/settings.json", "w"))

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.handleInput)
        thread.start()
        self.renderMessages()
        self.send()

if __name__ == "__main__":
    client = Client("127.0.0.1", 5000)
    client.run()