import customtkinter as ctk
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ChatLink")
        self.iconbitmap("./assets/icon.ico")
        self.geometry("800x480")
        self.minsize(800, 480)
        self.resizable(True, True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.config(bg="grey15")
        self.initWidgets()

    def initWidgets(self):
        # Ressources
        sendIcon = ctk.CTkImage(Image.open("./assets/send.png"))

        # Tabs
        self.tabView = ctk.CTkTabview(self, anchor="nw", fg_color="grey20")
        self.tabView.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.friendsTab = self.tabView.add("Friends")
        self.groupsTab = self.tabView.add("Groups")
        # self.menuTab = self.tabView.add("Settings")

        # Friends Tab
        self.friendsTab.grid_rowconfigure(0, weight=20)
        self.friendsTab.grid_rowconfigure(1, weight=1)
        self.friendsTab.grid_columnconfigure(0, weight=1)
        self.friendsTab.grid_columnconfigure(1, weight=8)

        self.friendsTab_friendsFrame = ctk.CTkScrollableFrame(self.friendsTab, width=150, fg_color="grey15")
        self.friendsTab_friendsFrame.grid(row=0, column=0, rowspan=2, padx=5, pady=(0, 5), sticky="nsew")

        self.friendsTab_chatFrame = ctk.CTkScrollableFrame(self.friendsTab, fg_color="grey15")
        self.friendsTab_chatFrame.grid(row=0, column=1, columnspan=2, padx=5, pady=(0, 5), sticky="nsew")

        self.friendsTab_inputFrame = ctk.CTkFrame(self.friendsTab, fg_color="grey15", height=30)
        self.friendsTab_inputFrame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.friendsTab_inputFrame.grid_columnconfigure(0, weight=8)
        self.friendsTab_inputFrame.grid_columnconfigure(1, weight=1)
        self.friendsTab_inputFrame.grid_rowconfigure(0, weight=1)

        self.friendsTab_inputEntry = ctk.CTkTextbox(self.friendsTab_inputFrame, height=20, fg_color="grey20")
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

        self.groupsTab_channelFrame = ctk.CTkScrollableFrame(self.groupsTab, width=150, fg_color="grey15")
        self.groupsTab_channelFrame.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")

        self.groupsTab_chatFrame = ctk.CTkScrollableFrame(self.groupsTab, fg_color="grey15")
        self.groupsTab_chatFrame.grid(row=0, column=1, rowspan=2, padx=5, pady=(0, 5), sticky="nsew")

        self.groupsTab_inputFrame = ctk.CTkFrame(self.groupsTab, fg_color="grey15", height=30)
        self.groupsTab_inputFrame.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.groupsTab_inputFrame.grid_columnconfigure(0, weight=8)
        self.groupsTab_inputFrame.grid_columnconfigure(1, weight=1)
        self.groupsTab_inputFrame.grid_rowconfigure(0, weight=1)

        self.groupsTab_inputEntry = ctk.CTkTextbox(self.groupsTab_inputFrame, height=20, fg_color="grey20")
        self.groupsTab_inputEntry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.groupsTab_inputButton = ctk.CTkButton(self.groupsTab_inputFrame, text="", image=sendIcon, corner_radius=5, width=10, height=10)
        self.groupsTab_inputButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()