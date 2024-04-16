import customtkinter as ctk
import socket
import os
import json
from PIL import Image
from datetime import datetime
from classes.FloatingMenu import FloatingMenu

class Network:
    def __init__(self, host:str, port:int):
        self.HOST = host
        self.PORT = port
        self._BUFFER = 1024
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connected = False

    def connect(self, username:str):
        try:
            self._client.connect((self._HOST, self._PORT))
            self._connected = True
            return (f"Connected to server at {self._HOST}:{self._PORT}", self.send(username))
        except Exception as e:
            return e

    def disconnect(self):
        self._client.close()
        self._connected = False
        return "Disconnected from server"

    def send(self, data:dict):
        try:
            self._client.send(str(data).encode("utf-8"))
            return self._client.recv(self._BUFFER).decode("utf-8")
        except socket.error as e:
            return e

class App(ctk.CTk):
    def __init__(self):
        super().__init__() # Init ctk
        self.title("ChatLink")
        self.iconbitmap("./assets/icon.ico")
        self.geometry("800x480")
        self.minsize(800, 480)
        self.resizable(True, True)
        self.config(bg="grey15")

        self._MAX_MESSAGE = 100 # Usufull variables for ctk
        self._RESIZING = False
        self.friendsMessages = {}
        self.groupsMessages = {}

        self.grid_rowconfigure(0, weight=1) # Init Widgets
        self.grid_columnconfigure(0, weight=1)
        self.initWidgets()
        self.bind("<Configure>", self.resizeRequest)

        if not os.path.exists("./data"): # Initialize user data
            os.mkdir("./data")
            json.dump({}, open("./data/settings.json", "w"))
            json.dump({}, open("./data/groups.json", "w"))
            json.dump({}, open("./data/privateMessages.json", "w"))

        self.username = "OJd_dJO"
        self.msg = {
            "type": "none",
            "sender": self.username,
            "group": "",
            "recipient": "",
        }
        self.network = Network("", 0)

    def sendPrivateMessage(self):
        self.msg["type"] = "private"
        self.msg["recipient"] = "OJd_dJO"
        self.msg["message"] = self.friendsTab_inputEntry.get("1.0", ctk.END)
        self.sendData(self.makeData())

    # def sendGroupMessage(self):
    #     self.msg["type"] = "group"
    #     self.msg["group"] = ""
    #     self.msg["recipient"] = ""
    #     self.msg["message"] = self.groupsTab_inputEntry.get("1.0", ctk.END)
    #     self.sendData(self.makeData())

    def sendData(self, data:dict):
        return self.network.send(data)

    def makeData(self):
        return {
            "msg": self.msg,
            "username": self.msg["sender"]
        }

    def initWidgets(self):
        # Ressources
        sendIcon = ctk.CTkImage(Image.open("./assets/send.png"))

        # Tabs
        self.tabView = ctk.CTkTabview(self, anchor="nw", fg_color="grey20")
        self.tabView.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.friendsTab = self.tabView.add("Friends")
        self.groupsTab = self.tabView.add("Groups")
        self.settingsTab = self.tabView.add("Settings")

        # Friends Tab
        self.friendsTab.grid_rowconfigure(0, weight=20)
        self.friendsTab.grid_rowconfigure(1, weight=1)
        self.friendsTab.grid_columnconfigure(0, weight=1)
        self.friendsTab.grid_columnconfigure(1, weight=8)

        self.friendsTab_friendsFrame = ctk.CTkScrollableFrame(self.friendsTab, width=150, fg_color="grey15")
        self.friendsTab_friendsFrame.grid(row=0, column=0, rowspan=2, padx=5, pady=(0, 5), sticky="nsew")
        self.friendsTab_friendsFrame.grid_columnconfigure(0, weight=1)

        self.friendsTab_chatFrame = ctk.CTkScrollableFrame(self.friendsTab, fg_color="grey15")
        self.friendsTab_chatFrame.grid(row=0, column=1, columnspan=2, padx=5, pady=(0, 5), sticky="nsew")
        self.friendsTab_chatFrame.grid_columnconfigure(0, weight=1)

        self.friendsTab_inputFrame = ctk.CTkFrame(self.friendsTab, fg_color="grey15", height=50)
        self.friendsTab_inputFrame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.friendsTab_inputFrame.grid_columnconfigure(0, weight=8)
        self.friendsTab_inputFrame.grid_rowconfigure(0, weight=1)

        self.friendsTab_inputEntry = ctk.CTkTextbox(self.friendsTab_inputFrame, height=40, fg_color="grey20")
        self.friendsTab_inputEntry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.friendsTab_inputButton = ctk.CTkButton(self.friendsTab_inputFrame, text="", image=sendIcon, corner_radius=5, width=10, height=10)
        self.friendsTab_inputButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        # Groups Tab
        self.groupsTab.grid_rowconfigure(0, weight=1)
        self.groupsTab.grid_rowconfigure(1, weight=20)
        self.groupsTab.grid_rowconfigure(2, weight=1)
        self.groupsTab.grid_columnconfigure(0, weight=1)
        self.groupsTab.grid_columnconfigure(1, weight=8)

        self.groupsTab_groupsFrame = ctk.CTkScrollableFrame(self.groupsTab, width=150, fg_color="grey15")
        self.groupsTab_groupsFrame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.groupsTab_groupsFrame.grid_columnconfigure(0, weight=1)

        self.groupsTab_channelFrame = ctk.CTkScrollableFrame(self.groupsTab, width=150, fg_color="grey15")
        self.groupsTab_channelFrame.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.groupsTab_channelFrame.grid_columnconfigure(0, weight=1)

        self.groupsTab_chatFrame = ctk.CTkScrollableFrame(self.groupsTab, fg_color="grey15")
        self.groupsTab_chatFrame.grid(row=0, column=1, rowspan=2, padx=5, pady=(0, 5), sticky="nsew")
        self.groupsTab_chatFrame.grid_columnconfigure(0, weight=1)

        self.groupsTab_inputFrame = ctk.CTkFrame(self.groupsTab, fg_color="grey15", height=50)
        self.groupsTab_inputFrame.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.groupsTab_inputFrame.grid_columnconfigure(0, weight=8)
        self.groupsTab_inputFrame.grid_rowconfigure(0, weight=1)

        self.groupsTab_inputEntry = ctk.CTkTextbox(self.groupsTab_inputFrame, height=40, fg_color="grey20")
        self.groupsTab_inputEntry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.groupsTab_inputButton = ctk.CTkButton(self.groupsTab_inputFrame, text="", image=sendIcon, corner_radius=5, width=10, height=10)
        self.groupsTab_inputButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        # Settings Tab
        self.settingsTab.grid_rowconfigure(0, weight=1)
        self.settingsTab.grid_columnconfigure(0, weight=1)

        self.settingsTab_tabview = ctk.CTkTabview(self.settingsTab, anchor="nw", fg_color="grey15")
        self.settingsTab_tabview.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_generalTab = self.settingsTab_tabview.add("General")
        self.settingsTab_serverTab = self.settingsTab_tabview.add("Server")
        self.settingsTab_appearanceTab = self.settingsTab_tabview.add("Appearance")
        self.settingsTab_aboutTab = self.settingsTab_tabview.add("About")
        #Server Tab
        self.settingsTab_serverTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_serverTab.grid_rowconfigure(1, weight=1)
        self.settingsTab_serverInfo = ctk.CTkFrame(self.settingsTab_serverTab, fg_color="grey15", border_width=2, corner_radius=5)
        self.settingsTab_serverInfo.grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="nsew")
        self.settingsTab_serverInfo.grid_columnconfigure(0, weight=1)
        self.settingsTab_serverLabel = ctk.CTkLabel(self.settingsTab_serverInfo, text="Server Information", fg_color="grey20", corner_radius=5)
        self.settingsTab_serverLabel.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.settingsTab_IPEntry = ctk.CTkEntry(self.settingsTab_serverInfo, fg_color="grey20", placeholder_text="IP")
        self.settingsTab_IPEntry.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_portEntry = ctk.CTkEntry(self.settingsTab_serverInfo, fg_color="grey20", placeholder_text="Port")
        self.settingsTab_portEntry.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_connectButton = ctk.CTkButton(self.settingsTab_serverInfo, text="Connect", corner_radius=5, command=self.connectToServer)
        self.settingsTab_connectButton.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="se")
        self.settingsTab_disconnectButton = ctk.CTkButton(self.settingsTab_serverInfo, text="Disconnect", corner_radius=5, command=self.disconnectFromServer)
        self.settingsTab_disconnectButton.grid(row=4, column=1, padx=(0, 10), pady=(0, 10), sticky="se")
        self.settingsTab_logFrame = ctk.CTkFrame(self.settingsTab_serverTab, fg_color="grey15", border_width=2, corner_radius=5)
        self.settingsTab_logFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.settingsTab_logFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_logFrame.grid_rowconfigure(1, weight=1)
        self.settingsTab_logLabel = ctk.CTkLabel(self.settingsTab_logFrame, text="Logs", fg_color="grey20", corner_radius=5)
        self.settingsTab_logLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_log = ctk.CTkTextbox(self.settingsTab_logFrame, fg_color="grey20", height=80, wrap="word")
        self.settingsTab_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Test (Message with long text)
        self.addFriendMessage("OJd_dJO", "OJd_dJO", "16/04/2024 11:51", "Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

    def createUserUI(self):
        window = FloatingMenu(300, 200)
        window.unbind("<FocusOut>")
        window.unbind("<Escape>")

        mainFrame = ctk.CTkFrame(window, fg_color="grey15")
        mainFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        usernameInput = ctk.CTkEntry(mainFrame, fg_color="grey20", placeholder_text="Username")
        usernameInput.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        confirmButton = ctk.CTkButton(mainFrame, text="Confirm", corner_radius=5)
        confirmButton.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def connectToServer(self):
        ip = self.settingsTab_IPEntry.get()
        port = self.settingsTab_portEntry.get()
        if ip == "" or port == "":
            self.settingsTab_log.insert(ctk.END, "Please enter IP and Port\n")
            return
        self.network.HOST = ip
        self.network.PORT = int(port)
        data = self.network.connect("OJd_dJO") #test
        self.settingsTab_log.insert(ctk.END, f"{data[0]}\n")
        self.settingsTab_log.insert(ctk.END, f"{data[1]}\n")

    def disconnectFromServer(self):
        data = self.network.disconnect()
        self.settingsTab_log.insert(ctk.END, f"{data}\n")

    def addFriendMessage(self, friend:str, sender:str, date:str, message:str):
        today = datetime.now().strftime("%d/%m/%Y")
        date = date.split(" ")[1] if date.split(" ")[0] == today else date
        msg = ctk.CTkLabel(self.friendsTab_chatFrame, text=f"{sender}       {date}\n{message}", fg_color="grey20", corner_radius=5, anchor="w", justify="left")
        msg.grid(row=len(self.friendsMessages), column=0, padx=5, pady=5, sticky="nsew")
        msg.configure(wraplength=msg.winfo_width()-10)

        def createSelectable(event:any):
            window = FloatingMenu(msg.winfo_width()+20, msg.winfo_height()+40, msg.winfo_rootx()-10, msg.winfo_rooty()-10)
            textbox = ctk.CTkTextbox(window, fg_color="grey20", wrap="word")
            textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            textbox.insert("1.0", msg.cget("text"))
            textbox.configure(state="disabled")

        def createMenu(event:any):
            window = FloatingMenu(150, 200, event.x_root, event.y_root)
            mainFrame = ctk.CTkFrame(window, fg_color="grey20")
            mainFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            mainFrame.grid_columnconfigure(0, weight=1)

            copyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            copyFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyFrame.grid_columnconfigure(0, weight=1)
            copyButton = ctk.CTkButton(copyFrame, text="Copy All", fg_color="grey15", corner_radius=5)
            copyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyMessageButton = ctk.CTkButton(copyFrame, text="Copy Message", fg_color="grey15", corner_radius=5)
            copyMessageButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            replyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            replyFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            replyFrame.grid_columnconfigure(0, weight=1)
            replyButton = ctk.CTkButton(replyFrame, text="Reply", fg_color="grey15", corner_radius=5)
            replyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            window.bind("<Button-1>", lambda event: window.after(100, window.destroy))
            def copyAll(event:any):
                self.clipboard_clear()
                self.clipboard_append(msg.cget("text"))
                self.update()
            copyButton.bind("<Button-1>", copyAll)
            def copyMessage(event:any):
                self.clipboard_clear()
                text = msg.cget("text").split("\n")[1:]
                self.clipboard_append("\n".join(text))
                self.update()
            copyMessageButton.bind("<Button-1>", copyMessage)
            def reply(event:any):
                self.friendsTab_inputEntry.insert("1.0", f"@{sender} ")
            replyButton.bind("<Button-1>", reply)

        msg.bind("<Double-Button-1>", createSelectable)
        msg.bind("<Button-3>", createMenu)
        if friend not in self.friendsMessages:
            self.friendsMessages[friend] = []
        self.friendsMessages[friend].append(msg)
        if len(self.friendsMessages[friend]) > self._MAX_MESSAGE:
            self.friendsMessages[friend][0].destroy()
            self.friendsMessages[friend].pop(0)

    # Handle main window resize event
    def resizeRequest(self, event:any):
        def setResizingFalse():
            self._RESIZING = False
        if not self._RESIZING:
            self._RESIZING = True
            self.after(100, setResizingFalse)
            self.after(150, self.resize)
    def resize(self):
        if self._RESIZING:
            return
        for friend in self.friendsMessages:
            for msg in self.friendsMessages[friend]:
                # resize message only if visible
                if msg.winfo_viewable():
                    msg.configure(wraplength=msg.winfo_width()-10)


if __name__ == "__main__":
    app = App()
    app.mainloop()