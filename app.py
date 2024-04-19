import customtkinter as ctk
import socket
import os
import json
import threading
from PIL import Image
from datetime import datetime
from classes.FloatingMenu import FloatingMenu

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

        # Initialize network client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._BUFFER = 1024

        self.path = f"./data" # Initialize data
        if not os.path.exists(self.path): # Initialize user data
            os.mkdir(self.path)
            json.dump({}, open("./data/privateMessages.json", "w"))
            json.dump({}, open("./data/groups.json", "w"))
            json.dump({}, open("./data/settings.json", "w"))
            self.username = ""
            self._HOST = "" # Set default values for settings
            self._PORT = ""
        else:
            settings = json.load(open(f"./data/settings.json")) # Load settings
            if "username" not in settings:
                self.username = ""
            else:
                self.username = settings["username"]
                self.settingsTab_usernameEntry.insert(ctk.END, settings["username"])
                self.settingsTab_usernameEntry.configure(state="disabled")
                self.settingsTab_usernameButton.configure(state="disabled")
            if "ip" in settings and "port" in settings:
                if settings["ip"] != "" and settings["port"] != "":
                    self.settingsTab_IPEntry.insert(ctk.END, settings["ip"])
                    self.settingsTab_portEntry.insert(ctk.END, settings["port"])
                    self._HOST = settings["ip"]
                    self._PORT = int(settings["port"])
                    log = self.client.connect()
                    self.settingsTab_log.insert(ctk.END, log + "\n")
                else :
                    self._HOST = ""
                    self._PORT = ""
            else:
                self._HOST = ""
                self._PORT = ""

        self.privateMessages = json.load(open(f"{self.path}/privateMessages.json"))
        self.groups = json.load(open(f"{self.path}/groups.json"))
        self.privateMessagesWidgets = []
        self.groupsChannelsWidgets = []
        self.groupsMessagesWidgets = []
        self.currentGroup = "private"
        self.currentChannel = ""
        self.msg = {
            "sender": self.username,
            "group": self.currentGroup,
            "channel": self.currentChannel,
            "message": ""
        }

    # Network
    def connect(self):
        self._HOST = self.settingsTab_IPEntry.get()
        self._PORT = int(self.settingsTab_portEntry.get())
        try:
            self.client.connect((self._HOST, self._PORT))
        except Exception as e:
            self.settingsTab_log.insert(ctk.END, f"Error: {e}\n")
            return
        try:
            self.client.send(self.username.encode("utf-8"))
            self.settingsTab_log.insert(ctk.END, self.client.recv(self._BUFFER).decode("utf-8") + "\n")
        except Exception as e:
            self.settingsTab_log.insert(ctk.END, f"Error: {e}\n")
            return
        self.saveSettings()
        threading.Thread(target=self.send).start()
    
    def send(self):
        while True:
            data = str({
                "msg": self.msg,
                "username": self.username,
                "group": self.currentGroup,
                "channel": self.currentChannel
            })
            self.client.send(data.encode("utf-8"))
            self.msg["message"] = ""
            self.manageData(self.client.recv(self._BUFFER).decode("utf-8"))

    def manageData(self, data):
        try:
            data = eval(data)
            if self.currentGroup == "private": # Private
                if data[0] not in self.privateMessages: # Create channel if not exists and add all the messages
                    self.privateMessages[data[0]] = data[1]
                    for element in data[1]:
                        self.addFriendMessage(element["sender"], element["time"], element["message"])
                    self.saveData()
                else: # Else add messages to channel
                    changes = False
                    for element in data[1]:
                        if element not in self.privateMessages[data[0]]:
                            changes = True
                            self.privateMessages[data[0]].append(element)
                            if len(self.privateMessages[data[0]]) > 100:
                                self.privateMessages[data[0]].pop(0)
                            self.addFriendMessage(element["sender"], element["time"], element["message"])
                    if changes:
                        self.saveData()
            else: # Group
                if self.currentGroup not in self.groups: # Create group if not exists
                    self.groups[self.currentGroup] = {}
                if data[0] not in self.groups[self.currentGroup]: # Create channel if not exists and add all the messages
                    self.groups[self.currentGroup][data[0]] = data[1]
                    for element in data[1]:
                        self.addGroupMessage(element["sender"], element["time"], element["message"])
                    self.saveData()
                else: # Else add messages to channel
                    changes = False
                    for element in data[1]:
                        if element not in self.groups[self.currentGroup][data[0]]:
                            changes = True
                            self.groups[self.currentGroup][data[0]].append(element)
                            if len(self.groups[self.currentGroup][data[0]]) > 100:
                                self.groups[self.currentGroup][data[0]].pop(0)
                            self.addGroupMessage(element["sender"], element["time"], element["message"])
                    if changes:
                        self.saveData()
        except Exception as e:
            pass

    def renderMessages(self):
        if self.currentGroup == "private":
            channel = ",".join(sorted([self.username, self.currentChannel]))
            if channel in self.privateMessages:
                for message in self.privateMessages[channel]:
                    self.addFriendMessage(message["sender"], message["time"], message["message"])
        if self.currentGroup in self.groups:
            if self.currentChannel in self.groups[self.currentGroup]:
                for message in self.groups[self.currentGroup][self.currentChannel]:
                    self.addGroupMessage(message["sender"], message["time"], message["message"])

    def setMessage(self, message:str):
        self.msg["message"] = message

    def setCurrentGroup(self, group:str):
        self.currentGroup = group

    def setCurrentChannel(self, channel:str):
        self.currentChannel = channel

    def saveSettings(self):
        settings = {
            "username": self.settingsTab_usernameEntry.get(),
            "ip": self.settingsTab_IPEntry.get(),
            "port": self.settingsTab_portEntry.get()
        }
        json.dump(settings, open(f"./data/settings.json", "w"))

    def saveData(self):
        json.dump(self.privateMessages, open("./data/privateMessages.json", "w"))
        json.dump(self.groups, open("./data/groups.json", "w"))

    def saveUsername(self):
        self.saveSettings()
        self.settingsTab_usernameEntry.configure(state="disabled")
        self.settingsTab_usernameButton.configure(state="disabled")

    # UI
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
        # General Tab
        self.settingsTab_generalTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_usernameEntry = ctk.CTkEntry(self.settingsTab_generalTab, fg_color="grey20", placeholder_text="Username (WARNING: Can't be changed after saving)")
        self.settingsTab_usernameEntry.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.settingsTab_usernameButton = ctk.CTkButton(self.settingsTab_generalTab, text="Save", corner_radius=5, command=self.saveSettings)
        self.settingsTab_usernameButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        # Server Tab
        self.settingsTab_serverTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_serverTab.grid_rowconfigure(1, weight=1)
        self.settingsTab_serverInfo = ctk.CTkFrame(self.settingsTab_serverTab, fg_color="grey15", border_width=2, corner_radius=5)
        self.settingsTab_serverInfo.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.settingsTab_serverInfo.grid_columnconfigure(0, weight=1)
        self.settingsTab_serverLabel = ctk.CTkLabel(self.settingsTab_serverInfo, text="Server Information", fg_color="grey20", corner_radius=5)
        self.settingsTab_serverLabel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_IPEntry = ctk.CTkEntry(self.settingsTab_serverInfo, fg_color="grey20", placeholder_text="IP")
        self.settingsTab_IPEntry.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_portEntry = ctk.CTkEntry(self.settingsTab_serverInfo, fg_color="grey20", placeholder_text="Port")
        self.settingsTab_portEntry.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_connectButton = ctk.CTkButton(self.settingsTab_serverInfo, text="Connect", corner_radius=5, command=self.connect)
        self.settingsTab_connectButton.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="se")
        self.settingsTab_logFrame = ctk.CTkFrame(self.settingsTab_serverTab, fg_color="grey15", border_width=2, corner_radius=5)
        self.settingsTab_logFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.settingsTab_logFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_logFrame.grid_rowconfigure(1, weight=1)
        self.settingsTab_logLabel = ctk.CTkLabel(self.settingsTab_logFrame, text="Logs", fg_color="grey20", corner_radius=5)
        self.settingsTab_logLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_log = ctk.CTkTextbox(self.settingsTab_logFrame, fg_color="grey20", height=80, wrap="word")
        self.settingsTab_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Test (Message with long text)
        # self.addFriendMessage("OJd_dJO", "OJd_dJO", "16/04/2024 11:51", "Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

    def addFriendMessage(self, sender:str, date:str, message:str):
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
            copyButton = ctk.CTkButton(copyFrame, text="Copy All", fg_color="grey15", corner_radius=5, command=copyAll)
            copyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyMessageButton = ctk.CTkButton(copyFrame, text="Copy Message", fg_color="grey15", corner_radius=5, command=copyMessage)
            copyMessageButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            replyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            replyFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            replyFrame.grid_columnconfigure(0, weight=1)
            replyButton = ctk.CTkButton(replyFrame, text="Reply", fg_color="grey15", corner_radius=5, command=reply)
            replyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            window.bind("<Button-1>", lambda event: window.after(100, window.destroy))
            def copyAll():
                self.clipboard_clear()
                self.clipboard_append(msg.cget("text"))
                self.update()
            def copyMessage():
                self.clipboard_clear()
                text = msg.cget("text").split("\n")[1:]
                self.clipboard_append("\n".join(text))
                self.update()
            def reply():
                text = msg.cget("text").split("\n")
                for i in range(len(text)):
                    text[i] = "│    " + text[i]
                    self.friendsTab_inputEntry.insert(f"{i+1}.0", text[i] + "\n")
                self.friendsTab_inputEntry.insert(ctk.END, "└─\n")
                self.friendsTab_inputEntry.see(ctk.END)
                self.friendsTab_inputEntry.focus()

        msg.bind("<Double-Button-1>", createSelectable)
        msg.bind("<Button-3>", createMenu)

    def addGroupMessage(self, sender:str, date:str, message:str):
        today = datetime.now().strftime("%d/%m/%Y")
        date = date.split(" ")[1] if date.split(" ")[0] == today else date
        msg = ctk.CTkLabel(self.groupsTab_chatFrame, text=f"{sender}       {date}\n{message}", fg_color="grey20", corner_radius=5, anchor="w", justify="left")
        msg.grid(row=len(self.groupsMessages), column=0, padx=5, pady=5, sticky="nsew")
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
            copyButton = ctk.CTkButton(copyFrame, text="Copy All", fg_color="grey15", corner_radius=5, command=copyAll)
            copyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyMessageButton = ctk.CTkButton(copyFrame, text="Copy Message", fg_color="grey15", corner_radius=5, command=copyMessage)
            copyMessageButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            replyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            replyFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            replyFrame.grid_columnconfigure(0, weight=1)
            replyButton = ctk.CTkButton(replyFrame, text="Reply", fg_color="grey15", corner_radius=5, command=reply)
            replyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            window.bind("<Button-1>", lambda event: window.after(100, window.destroy))
            def copyAll():
                self.clipboard_clear()
                self.clipboard_append(msg.cget("text"))
                self.update()
            def copyMessage():
                self.clipboard_clear()
                text = msg.cget("text").split("\n")[1:]
                self.clipboard_append("\n".join(text))
                self.update()
            def reply():
                text = msg.cget("text").split("\n")
                for i in range(len(text)):
                    text[i] = "│    " + text[i]
                    self.groupsTab_inputEntry.insert(f"{i+1}.0", text[i] + "\n")
                self.groupsTab_inputEntry.insert(ctk.END, "└─\n")
                self.groupsTab_inputEntry.see(ctk.END)
                self.groupsTab_inputEntry.focus()

        msg.bind("<Double-Button-1>", createSelectable)
        msg.bind("<Button-3>", createMenu)

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

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.mainloop()