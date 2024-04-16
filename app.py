import customtkinter as ctk
from PIL import Image
from datetime import datetime
from classes.FloatingMenu import FloatingMenu

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ChatLink")
        self.iconbitmap("./assets/icon.ico")
        self.geometry("800x480")
        self.minsize(800, 480)
        self.resizable(True, True)
        self.config(bg="grey15")

        self._MAX_MESSAGE = 100
        self._RESIZING = False
        self.friendsMessages = {}
        self.groupsMessages = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.initWidgets()

        self.bind("<Configure>", self.resizeRequest)

    def initWidgets(self):
        # Ressources
        sendIcon = ctk.CTkImage(Image.open("./assets/send.png"))

        # Tabs
        self.tabView = ctk.CTkTabview(self, anchor="nw", fg_color="grey20")
        self.tabView.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.friendsTab = self.tabView.add("Friends")
        self.groupsTab = self.tabView.add("Groups")
        self.menuTab = self.tabView.add("Settings")

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

        self.groupsTab_groupsFrame = ctk.CTkScrollableFrame(self.groupsTab, fg_color="grey15")
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

        # Test (Message with long text)
        self.addFriendMessage("OJd_dJO", "OJd_dJO", "16/04/2024 11:51", "Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

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