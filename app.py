import customtkinter as ctk
import socket
import os
import sys
import json
import threading
from PIL import Image
from datetime import datetime
from classes.FloatingMenu import FloatingMenu
from classes.NotificationPopup import NotificationPopup

class App(ctk.CTk):
    def __init__(self):
        super().__init__(("grey80", "grey15")) # Init ctk
        self.title("ChatLink")
        self.iconbitmap("./assets/icon.ico")
        self.geometry("800x480")
        self.minsize(800, 480)
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")

        self._MAX_MESSAGE = 100 # Init variables
        self.runNetwork = True
        self._RESIZING = False
        self.currentGroup = "private"
        self.currentChannel = ""
        self.message = ""

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
                if self.username != "":
                    self.settingsTab_usernameEntry.insert(ctk.END, settings["username"])
                    self.settingsTab_usernameEntry.configure(state="disabled")
                    self.settingsTab_usernameButton.configure(state="disabled")
            if "ip" in settings and "port" in settings:
                if settings["ip"] != "" and settings["port"] != "":
                    self.settingsTab_IPEntry.insert(ctk.END, settings["ip"])
                    self.settingsTab_portEntry.insert(ctk.END, settings["port"])
                    self._HOST = settings["ip"]
                    self._PORT = int(settings["port"])
                    self.connect()
                else :
                    self._HOST = ""
                    self._PORT = ""
            else:
                self._HOST = ""
                self._PORT = ""
            if "theme" in settings:
                self.theme.set(settings["theme"])
                ctk.set_appearance_mode(settings["theme"])
                if settings["theme"] == "dark":
                    self.settingsTab_switchTheme.select()
                elif settings["theme"] == "light":
                    self.settingsTab_switchTheme.deselect()
            else:
                self.settingsTab_switchTheme.select()

        self.privateMessages = json.load(open(f"{self.path}/privateMessages.json"))
        self.groups = json.load(open(f"{self.path}/groups.json"))

        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.runNetwork = False
        self.client.close()
        self.destroy()
        sys.exit(0)

    # Network
    def connect(self):
        if self.username == "": # Check if username is set
            self.settingsTab_log.insert(ctk.END, "Error: Username not set\n")
        else:
            try:
                self._HOST = self.settingsTab_IPEntry.get()
            except Exception as e:
                self.settingsTab_log.insert(ctk.END, f"Error: IP: {e}\n")
                return
            try:
                self._PORT = int(self.settingsTab_portEntry.get())
            except Exception as e:
                self.settingsTab_log.insert(ctk.END, f"Error: Port: {e}\n")
                return
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
            self.saveServerInfo()
            threading.Thread(target=self.send).start()

    def send(self):
        while self.runNetwork:
            data = str({
                "msg": {
                    "sender": self.username,
                    "group": self.currentGroup,
                    "channel": self.currentChannel,
                    "message": self.message
                },
                "username": self.username,
                "group": self.currentGroup,
                "channel": self.currentChannel
            })
            self.client.send(data.encode("utf-8"))
            self.message = ""
            self.manageData(self.client.recv(self._BUFFER).decode("utf-8"))

    def manageData(self, data):
        currentGroup = self.currentGroup
        currentChannel = self.currentChannel
        try:
            data = eval(data)
            if currentGroup == "private": # Private
                if data[0] not in self.privateMessages: # Create channel if not exists and add all the messages
                    self.privateMessages[data[0]] = data[1]
                    for element in data[1]:
                        if self.currentGroup != currentGroup or self.currentChannel != element["channel"] or self.currentChannel != currentChannel:
                            return
                        self.addFriendMessage(element["sender"], element["time"], element["message"])
                    if self.currentGroup == currentGroup and self.currentChannel == data[0] and self.currentChannel == currentChannel:
                        self.saveData()
                else: # Else add messages to channel
                    changes = False
                    for element in data[1]:
                        if element not in self.privateMessages[data[0]]:
                            if self.currentGroup == currentGroup and self.currentChannel == element["channel"] and self.currentChannel == currentChannel:
                                return
                            changes = True
                            self.privateMessages[data[0]].append(element)
                            if len(self.privateMessages[data[0]]) > 100:
                                self.privateMessages[data[0]].pop(0)
                            self.addFriendMessage(element["sender"], element["time"], element["message"])
                    if changes and self.currentGroup == currentGroup and self.currentChannel == data[0] and self.currentChannel == currentChannel:
                        self.saveData()
            else: # Group
                if currentGroup not in self.groups: # Create group if not exists
                    self.groups[currentGroup] = {}
                if data[0] not in self.groups[currentGroup]: # Create channel if not exists and add all the messages
                    self.groups[currentGroup][data[0]] = data[1]
                    for element in data[1]:
                        if self.currentGroup != currentGroup or self.currentChannel != element["channel"] or self.currentChannel != currentChannel:
                            return
                        self.addGroupMessage(element["sender"], element["time"], element["message"])
                    if self.currentGroup == currentGroup and self.currentChannel == data[0] and self.currentChannel == currentChannel:
                        self.saveData()
                else: # Else add messages to channel
                    changes = False
                    for element in data[1]:
                        if element not in self.groups[currentGroup][data[0]]:
                            if self.currentGroup == currentGroup and self.currentChannel == element["channel"] and self.currentChannel == currentChannel:
                                return
                            changes = True
                            self.groups[currentGroup][data[0]].append(element)
                            if len(self.groups[currentGroup][data[0]]) > 100:
                                self.groups[currentGroup][data[0]].pop(0)
                            self.addGroupMessage(element["sender"], element["time"], element["message"])
                    if changes and self.currentGroup == currentGroup and self.currentChannel == data[0] and self.currentChannel == currentChannel:
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

    def saveData(self):
        json.dump(self.privateMessages, open("./data/privateMessages.json", "w"))
        json.dump(self.groups, open("./data/groups.json", "w"))

    def saveUsername(self):
        self.username = self.settingsTab_usernameEntry.get()
        if self.username != "":
            if self.username.__contains__(","):
                NotificationPopup(self, "Username can't contain ','")
            else:
                settings = json.load(open(f"./data/settings.json"))
                settings["username"] = self.username
                json.dump(settings, open(f"./data/settings.json", "w"))
                self.settingsTab_usernameEntry.configure(state="disabled")
                self.settingsTab_usernameButton.configure(state="disabled")

    def saveServerInfo(self):
        settings = json.load(open(f"./data/settings.json"))
        settings["ip"] = self._HOST
        settings["port"] = self._PORT
        json.dump(settings, open(f"./data/settings.json", "w"))

    def saveTheme(self):
        settings = json.load(open(f"./data/settings.json"))
        settings["theme"] = self.theme.get()
        json.dump(settings, open(f"./data/settings.json", "w"))

    # UI
    def initWidgets(self):
        # Ressources
        sendIcon = ctk.CTkImage(Image.open("./assets/send.png"))

        # Tabs
        self.tabView = ctk.CTkTabview(self, anchor="nw", fg_color=("grey85", "grey20"))
        self.tabView.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.friendsTab = self.tabView.add("Friends")
        self.groupsTab = self.tabView.add("Groups")
        self.settingsTab = self.tabView.add("Settings")

        # Friends Tab
        self.friendsTab.grid_rowconfigure(0, weight=1)
        self.friendsTab.grid_rowconfigure(1, weight=20)
        self.friendsTab.grid_rowconfigure(2, weight=1)
        self.friendsTab.grid_columnconfigure(0, weight=1)
        self.friendsTab.grid_columnconfigure(1, weight=8)

        self.friendsTab_friendsFrame = ctk.CTkScrollableFrame(self.friendsTab, width=150, fg_color=("grey80", "grey15"))
        self.friendsTab_friendsFrame.grid(row=0, column=0, rowspan=3, padx=5, pady=(0, 5), sticky="nsew")
        self.friendsTab_friendsFrame.grid_columnconfigure(0, weight=1)

        self.friendsTab_addFriendButton = ctk.CTkButton(self.friendsTab_friendsFrame, text="Add Friend", corner_radius=5)
        self.friendsTab_addFriendButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.friendsTab_addFriendButton.bind("<Button-1>", self.addFriendWindow)

        self.friendsTab_titleBar = ctk.CTkLabel(self.friendsTab, text="", fg_color=("grey80", "grey15"), corner_radius=5)
        self.friendsTab_titleBar.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="nsew")
        self.friendsTab_chatFrame = ctk.CTkScrollableFrame(self.friendsTab, fg_color=("grey80", "grey15"))
        self.friendsTab_chatFrame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.friendsTab_chatFrame.grid_columnconfigure(0, weight=1)

        self.friendsTab_inputFrame = ctk.CTkFrame(self.friendsTab, fg_color=("grey80", "grey15"), height=50)
        self.friendsTab_inputFrame.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.friendsTab_inputFrame.grid_columnconfigure(0, weight=8)
        self.friendsTab_inputFrame.grid_rowconfigure(0, weight=1)

        self.friendsTab_inputEntry = ctk.CTkTextbox(self.friendsTab_inputFrame, height=40, fg_color=("grey85", "grey20"))
        self.friendsTab_inputEntry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.friendsTab_inputButton = ctk.CTkButton(self.friendsTab_inputFrame, text="", image=sendIcon, corner_radius=5, width=10, height=10, command=lambda: self.setMessage(self.friendsTab_inputEntry.get("1.0", "end-1c")))
        self.friendsTab_inputButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        # Groups Tab
        self.groupsTab.grid_rowconfigure(0, weight=1)
        self.groupsTab.grid_rowconfigure(1, weight=1)
        self.groupsTab.grid_columnconfigure(0, weight=1)
        self.groupsTab.grid_columnconfigure(1, weight=8)

        self.groupsTab_groupsFrame = ctk.CTkScrollableFrame(self.groupsTab, width=150, fg_color=("grey80", "grey15"))
        self.groupsTab_groupsFrame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.groupsTab_groupsFrame.grid_columnconfigure(0, weight=1)

        self.groupsTab_addGroupButton = ctk.CTkButton(self.groupsTab_groupsFrame, text="Add Group", corner_radius=5)
        self.groupsTab_addGroupButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.groupsTab_addGroupButton.bind("<Button-1>", self.addGroupWindow)

        self.groupsTab_channelFrame = ctk.CTkScrollableFrame(self.groupsTab, width=150, fg_color=("grey80", "grey15"))
        self.groupsTab_channelFrame.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.groupsTab_channelFrame.grid_columnconfigure(0, weight=1)

        self.groupsTab_addChannelButton = ctk.CTkButton(self.groupsTab_channelFrame, text="Add Channel", corner_radius=5)
        self.groupsTab_addChannelButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.groupsTab_addChannelButton.bind("<Button-1>", self.addChannelWindow)

        self.groupsTab_rightFrame = ctk.CTkFrame(self.groupsTab, fg_color=("grey85", "grey20"))
        self.groupsTab_rightFrame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.groupsTab_rightFrame.grid_columnconfigure(0, weight=1)
        self.groupsTab_rightFrame.grid_rowconfigure(0, weight=1)
        self.groupsTab_rightFrame.grid_rowconfigure(1, weight=20)
        self.groupsTab_rightFrame.grid_rowconfigure(2, weight=1)
        self.groupsTab_titleBar = ctk.CTkLabel(self.groupsTab_rightFrame, text="", fg_color=("grey80", "grey15"), corner_radius=5)
        self.groupsTab_titleBar.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.groupsTab_chatFrame = ctk.CTkScrollableFrame(self.groupsTab_rightFrame, fg_color=("grey80", "grey15"))
        self.groupsTab_chatFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.groupsTab_chatFrame.grid_columnconfigure(0, weight=1)

        self.groupsTab_inputFrame = ctk.CTkFrame(self.groupsTab_rightFrame, fg_color=("grey80", "grey15"), height=50)
        self.groupsTab_inputFrame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.groupsTab_inputFrame.grid_columnconfigure(0, weight=8)
        self.groupsTab_inputFrame.grid_rowconfigure(0, weight=1)

        self.groupsTab_inputEntry = ctk.CTkTextbox(self.groupsTab_inputFrame, height=40, fg_color=("grey85", "grey20"))
        self.groupsTab_inputEntry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.groupsTab_inputButton = ctk.CTkButton(self.groupsTab_inputFrame, text="", image=sendIcon, corner_radius=5, width=10, height=10, command=lambda: self.setMessage(self.groupsTab_inputEntry.get("1.0", "end-1c")))
        self.groupsTab_inputButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        # Settings Tab
        self.settingsTab.grid_rowconfigure(0, weight=1)
        self.settingsTab.grid_columnconfigure(0, weight=1)

        self.settingsTab_tabview = ctk.CTkTabview(self.settingsTab, anchor="nw", fg_color=("grey80", "grey15"))
        self.settingsTab_tabview.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_generalTab = self.settingsTab_tabview.add("General")
        self.settingsTab_serverTab = self.settingsTab_tabview.add("Server")
        self.settingsTab_appearanceTab = self.settingsTab_tabview.add("Appearance")
        self.settingsTab_aboutTab = self.settingsTab_tabview.add("About")
        # General Tab
        self.settingsTab_generalTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_usernameFrame = ctk.CTkFrame(self.settingsTab_generalTab, fg_color=("grey80", "grey15"), border_width=2, corner_radius=5)
        self.settingsTab_usernameFrame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.settingsTab_usernameFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_usernameLabel = ctk.CTkLabel(self.settingsTab_usernameFrame, text="Username", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_usernameLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_usernameEntry = ctk.CTkEntry(self.settingsTab_usernameFrame, fg_color=("grey85", "grey20"), placeholder_text="Username (WARNING: Can't be changed after saving unless reset)")
        self.settingsTab_usernameEntry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_usernameButton = ctk.CTkButton(self.settingsTab_usernameFrame, text="Save", corner_radius=5, command=self.saveUsername)
        self.settingsTab_usernameButton.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="se")
        self.settingsTab_resetFrame = ctk.CTkFrame(self.settingsTab_generalTab, fg_color=("grey80", "grey15"), border_width=2, corner_radius=5)
        self.settingsTab_resetFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.settingsTab_resetFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_resetLabel = ctk.CTkLabel(self.settingsTab_resetFrame, text="Reset", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_resetLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_resetButton = ctk.CTkButton(self.settingsTab_resetFrame, text="Reset All Data and Close App", fg_color="#910000", hover_color="#660000", corner_radius=5, command=self.resetData)
        self.settingsTab_resetButton.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        # Server Tab
        self.settingsTab_serverTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_serverTab.grid_rowconfigure(1, weight=1)
        self.settingsTab_serverInfo = ctk.CTkFrame(self.settingsTab_serverTab, fg_color=("grey80", "grey15"), border_width=2, corner_radius=5)
        self.settingsTab_serverInfo.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.settingsTab_serverInfo.grid_columnconfigure(0, weight=1)
        self.settingsTab_serverLabel = ctk.CTkLabel(self.settingsTab_serverInfo, text="Server Information", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_serverLabel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_IPEntry = ctk.CTkEntry(self.settingsTab_serverInfo, fg_color=("grey85", "grey20"), placeholder_text="IP")
        self.settingsTab_IPEntry.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_portEntry = ctk.CTkEntry(self.settingsTab_serverInfo, fg_color=("grey85", "grey20"), placeholder_text="Port")
        self.settingsTab_portEntry.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.settingsTab_connectButton = ctk.CTkButton(self.settingsTab_serverInfo, text="Connect", corner_radius=5, command=self.connect)
        self.settingsTab_connectButton.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="se")
        self.settingsTab_logFrame = ctk.CTkFrame(self.settingsTab_serverTab, fg_color=("grey80", "grey15"), border_width=2, corner_radius=5)
        self.settingsTab_logFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.settingsTab_logFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_logFrame.grid_rowconfigure(1, weight=1)
        self.settingsTab_logLabel = ctk.CTkLabel(self.settingsTab_logFrame, text="Logs", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_logLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_log = ctk.CTkTextbox(self.settingsTab_logFrame, fg_color=("grey85", "grey20"), height=80, wrap="word")
        self.settingsTab_log.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        # Appearance Tab
        self.settingsTab_appearanceTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_appearanceFrame = ctk.CTkFrame(self.settingsTab_appearanceTab, fg_color=("grey80", "grey15"), border_width=2, corner_radius=5)
        self.settingsTab_appearanceFrame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.settingsTab_appearanceFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_themeLabel = ctk.CTkLabel(self.settingsTab_appearanceFrame, text="Theme", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_themeLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.theme = ctk.StringVar(value=ctk.get_appearance_mode())
        self.settingsTab_switchTheme = ctk.CTkSwitch(self.settingsTab_appearanceFrame, text="Dark Mode", fg_color=("grey85", "grey20"), variable=self.theme, onvalue="dark", offvalue="light", corner_radius=5, command=self.changeTheme)
        self.settingsTab_switchTheme.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        # About Tab
        self.settingsTab_aboutTab.grid_columnconfigure(0, weight=1)
        self.settingsTab_aboutFrame = ctk.CTkFrame(self.settingsTab_aboutTab, fg_color=("grey80", "grey15"), border_width=2, corner_radius=5)
        self.settingsTab_aboutFrame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="nsew")
        self.settingsTab_aboutFrame.grid_columnconfigure(0, weight=1)
        self.settingsTab_aboutLabel = ctk.CTkLabel(self.settingsTab_aboutFrame, text="About", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_aboutLabel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_aboutIcon = ctk.CTkImage(Image.open("./assets/icon.png"), size=(100, 100))
        self.settingsTab_aboutIconLabel = ctk.CTkLabel(self.settingsTab_aboutFrame, text="", image=self.settingsTab_aboutIcon, corner_radius=5, height=100)
        self.settingsTab_aboutIconLabel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.settingsTab_aboutText = ctk.CTkLabel(self.settingsTab_aboutFrame, text="This is a simple chat application made with Python and Tkinter\n\nAuthor: OJd_dJO", fg_color=("grey85", "grey20"), corner_radius=5)
        self.settingsTab_aboutText.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    def changeTheme(self):
        ctk.set_appearance_mode(self.theme.get())
        self.saveTheme()

    # Reset data
    def resetData(self):
        self.client.close()
        os.remove(f"{self.path}/privateMessages.json")
        os.remove(f"{self.path}/groups.json")
        os.remove(f"{self.path}/settings.json")
        os.rmdir(self.path)
        sys.exit(0)

    # Friends/Groups management
    def initFriends(self):
        for friend in self.privateMessages:
            friend = friend.split(",")[1] if friend.split(",")[0] == self.username else friend.split(",")[0]
            friendButton = ctk.CTkButton(self.friendsTab_friendsFrame, text=friend, fg_color=("grey85", "grey20"), corner_radius=5)
            friendButton.grid(row=len(self.friendsTab_friendsFrame.winfo_children()), column=0, padx=5, pady=5, sticky="nsew")
            friendButton.bind("<Button-1>", lambda event: self.setCurrentPrivate(friend))

    def initGroups(self):
        for group in self.groups:
            groupButton = ctk.CTkButton(self.groupsTab_groupsFrame, text=group, fg_color=("grey85", "grey20"), corner_radius=5)
            groupButton.grid(row=len(self.groupsTab_groupsFrame.winfo_children()), column=0, padx=5, pady=5, sticky="nsew")
            groupButton.bind("<Button-1>", lambda event: self.setCurrentGroup(group))

    def initChannels(self):
        if self.currentGroup in self.groups:
            for channel in self.groups[self.currentGroup]:
                channelButton = ctk.CTkButton(self.groupsTab_channelFrame, text=channel, fg_color=("grey85", "grey20"), corner_radius=5)
                channelButton.grid(row=len(self.groupsTab_channelFrame.winfo_children()), column=0, padx=5, pady=5, sticky="nsew")
                channelButton.bind("<Button-1>", lambda event: self.setCurrentChannel(channel))

    def resetChannels(self):
        for channels in self.groupsTab_channelFrame.winfo_children()[1:]:
            channels.destroy()

    def addFriendWindow(self, event:any):
        window = FloatingMenu(200, 100, event.x_root, event.y_root)
        window.configure(fg_color=("grey80", "grey15"))
        entry = ctk.CTkEntry(window, fg_color=("grey85", "grey20"), placeholder_text="Friend")
        entry.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        button = ctk.CTkButton(window, text="Add", corner_radius=5, command=lambda: self.addFriend(entry.get()))
        button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        def closeWindow():
            if entry.get() != "":
                window.destroy()
        button.bind("<Button-1>", lambda event: window.after(100, closeWindow))

    def addFriend(self, friend:str):
        if friend != "":
            friendButton = ctk.CTkButton(self.friendsTab_friendsFrame, text=friend, fg_color=("grey85", "grey20"), corner_radius=5)
            nb = len(self.friendsTab_friendsFrame.winfo_children())
            friendButton.grid(row=nb, column=0, padx=5, pady=5, sticky="nsew")
            friendButton.bind("<Button-1>", lambda event: self.setCurrentPrivate(friend))
        else:
            NotificationPopup(self, "Friend can't be empty")

    def addGroupWindow(self, event:any):
        window = FloatingMenu(200, 100, event.x_root, event.y_root)
        window.config(bg=("grey80", "grey15"))
        entry = ctk.CTkEntry(window, fg_color=("grey85", "grey20"), placeholder_text="Group")
        entry.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        button = ctk.CTkButton(window, text="Add", corner_radius=5, command=lambda: self.addGroup(entry.get()))
        button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        def closeWindow():
            if entry.get() != "":
                window.destroy()
        button.bind("<Button-1>", lambda event: window.after(100, closeWindow))

    def addGroup(self, group:str):
        if group != "":
            groupButton = ctk.CTkButton(self.groupsTab_groupsFrame, text=group, fg_color=("grey85", "grey20"), corner_radius=5)
            nb = len(self.groupsTab_groupsFrame.winfo_children())
            groupButton.grid(row=nb, column=0, padx=5, pady=5, sticky="nsew")
            groupButton.bind("<Button-1>", lambda event: self.setCurrentGroup(group))
        else:
            NotificationPopup(self, "Group can't be empty")

    def addChannelWindow(self, event:any):
        window = FloatingMenu(200, 100, event.x_root, event.y_root)
        window.configure(fg_color=("grey80", "grey15"))
        entry = ctk.CTkEntry(window, fg_color=("grey85", "grey20"), placeholder_text="Channel")
        entry.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        button = ctk.CTkButton(window, text="Add", corner_radius=5, command=lambda: self.addChannel(entry.get()))
        button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        def closeWindow():
            if entry.get() != "":
                window.destroy()
        button.bind("<Button-1>", lambda event: window.after(100, closeWindow))

    def addChannel(self, channel:str):
        if channel != "":
            channelButton = ctk.CTkButton(self.groupsTab_channelFrame, text=channel, fg_color=("grey85", "grey20"), corner_radius=5)
            nb = len(self.groupsTab_channelFrame.winfo_children())
            channelButton.grid(row=nb, column=0, padx=5, pady=5, sticky="nsew")
            channelButton.bind("<Button-1>", lambda event: self.setCurrentChannel(channel))
        else:
            NotificationPopup(self, "Channel can't be empty")

    # Messages management
    def setMessage(self, message:str):
        self.message = message
        self.friendsTab_inputEntry.delete("1.0", ctk.END)
        self.groupsTab_inputEntry.delete("1.0", ctk.END)

    def setCurrentGroup(self, group:str):
        self.currentGroup = ""
        def delayCallback():
            self.currentGroup = group
            self.resetChannels()
            self.resetMessages()
            for channels in self.groupsTab_channelFrame.winfo_children()[1:]:
                channels.destroy()
            self.groupsTab_titleBar.configure(text=self.currentGroup)
            self.initChannels()
        self.after(100, delayCallback)

    def setCurrentChannel(self, channel:str):
        self.channel = ""
        def delayCallback():
            self.currentChannel = channel
            self.resetMessages()
            self.renderMessages()
            self.groupsTab_titleBar.configure(text=f"{self.currentGroup} - {self.currentChannel}")
        self.after(100, delayCallback)

    def setCurrentPrivate(self, channel:str):
        self.currentGroup = ""
        def delayCallback():
            self.currentGroup = "private"
            self.currentChannel = channel
            self.resetChannels()
            self.resetMessages()
            self.renderMessages()
            self.friendsTab_titleBar.configure(text=f"Private - {self.currentChannel}")
        self.after(100, delayCallback)

    def resetMessages(self):
        for messages in self.friendsTab_chatFrame.winfo_children():
            messages.destroy()
        for messages in self.groupsTab_chatFrame.winfo_children():
            messages.destroy()
        self.friendsTab_titleBar.configure(text="")
        self.groupsTab_titleBar.configure(text="")

    def addFriendMessage(self, sender:str, date:str, message:str):
        today = datetime.now().strftime("%d/%m/%Y")
        date = date.split(" ")[1] if date.split(" ")[0] == today else date
        msg = ctk.CTkLabel(self.friendsTab_chatFrame, text=f"{sender}       {date}\n{message}", fg_color=("grey85", "grey20"), corner_radius=5, anchor="w", justify="left")
        msg.grid(row=len(self.friendsTab_chatFrame.winfo_children()), column=0, padx=5, pady=5, sticky="nsew")
        msg.configure(wraplength=msg.winfo_width()-10)

        def createSelectable(event:any):
            window = FloatingMenu(msg.winfo_width()+20, msg.winfo_height()+40, msg.winfo_rootx()-10, msg.winfo_rooty()-10)
            textbox = ctk.CTkTextbox(window, fg_color=("grey85", "grey20"), wrap="word")
            textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            textbox.insert("1.0", msg.cget("text"))
            textbox.configure(state="disabled")

        def createMenu(event:any):
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

            window = FloatingMenu(150, 200, event.x_root, event.y_root)
            mainFrame = ctk.CTkFrame(window, fg_color=("grey85", "grey20"))
            mainFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            mainFrame.grid_columnconfigure(0, weight=1)

            copyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            copyFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyFrame.grid_columnconfigure(0, weight=1)
            copyButton = ctk.CTkButton(copyFrame, text="Copy All", fg_color=("grey80", "grey15"), corner_radius=5, command=copyAll)
            copyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyMessageButton = ctk.CTkButton(copyFrame, text="Copy Message", fg_color=("grey80", "grey15"), corner_radius=5, command=copyMessage)
            copyMessageButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            replyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            replyFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            replyFrame.grid_columnconfigure(0, weight=1)
            replyButton = ctk.CTkButton(replyFrame, text="Reply", fg_color=("grey80", "grey15"), corner_radius=5, command=reply)
            replyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            window.bind("<Button-1>", lambda event: window.after(100, window.destroy))

        msg.bind("<Double-Button-1>", createSelectable)
        msg.bind("<Button-3>", createMenu)

    def addGroupMessage(self, sender:str, date:str, message:str):
        today = datetime.now().strftime("%d/%m/%Y")
        date = date.split(" ")[1] if date.split(" ")[0] == today else date
        msg = ctk.CTkLabel(self.groupsTab_chatFrame, text=f"{sender}       {date}\n{message}", fg_color=("grey85", "grey20"), corner_radius=5, anchor="w", justify="left")
        msg.grid(row=len(self.groupsTab_chatFrame.winfo_children()), column=0, padx=5, pady=5, sticky="nsew")
        msg.configure(wraplength=msg.winfo_width()-10)

        def createSelectable(event:any):
            window = FloatingMenu(msg.winfo_width()+20, msg.winfo_height()+40, msg.winfo_rootx()-10, msg.winfo_rooty()-10)
            textbox = ctk.CTkTextbox(window, fg_color=("grey85", "grey20"), wrap="word")
            textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            textbox.insert("1.0", msg.cget("text"))
            textbox.configure(state="disabled")

        def createMenu(event:any):
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

            window = FloatingMenu(150, 200, event.x_root, event.y_root)
            mainFrame = ctk.CTkFrame(window, fg_color=("grey85", "grey20"))
            mainFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            mainFrame.grid_columnconfigure(0, weight=1)

            copyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            copyFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyFrame.grid_columnconfigure(0, weight=1)
            copyButton = ctk.CTkButton(copyFrame, text="Copy All", fg_color=("grey80", "grey15"), corner_radius=5, command=copyAll)
            copyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            copyMessageButton = ctk.CTkButton(copyFrame, text="Copy Message", fg_color=("grey80", "grey15"), corner_radius=5, command=copyMessage)
            copyMessageButton.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            replyFrame = ctk.CTkFrame(mainFrame, border_width=2, corner_radius=5)
            replyFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
            replyFrame.grid_columnconfigure(0, weight=1)
            replyButton = ctk.CTkButton(replyFrame, text="Reply", fg_color=("grey80", "grey15"), corner_radius=5, command=reply)
            replyButton.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            window.bind("<Button-1>", lambda event: window.after(100, window.destroy))

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
        if self.currentGroup == "private":
            for msg in self.friendsTab_chatFrame.winfo_children():
                # resize message only if visible
                if msg.winfo_viewable():
                    msg.configure(wraplength=msg.winfo_width()-10)
        else:
            for msg in self.groupsTab_chatFrame.winfo_children():
                # resize message only if visible
                if msg.winfo_viewable():
                    msg.configure(wraplength=msg.winfo_width()-10)

    def run(self):
        self.initFriends()
        self.initGroups()
        self.mainloop()


app = App()
app.run()