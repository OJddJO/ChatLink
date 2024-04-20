import customtkinter as ctk

class NotificationPopup(ctk.CTkToplevel):
    def __init__(self, parent, text):
        width = 150
        height = 50
        padding = 10
        x = parent.winfo_x() + parent.winfo_width() - (width + padding)
        y = parent.winfo_y() + parent.winfo_height() - (height + padding)
        super().__init__()
        self.overrideredirect(True)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.wm_attributes('-transparentcolor','#FFFFFF')
        self.configure(bg='#FFFFFF')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.notificationFrame = ctk.CTkFrame(self, bg_color=('grey80', 'grey15'), width=width-20, height=height-20, corner_radius=10)
        self.notificationFrame.grid(row=0, column=0, sticky='nsew')
        self.notificationFrame.grid_columnconfigure(0, weight=1)
        
        self.notificationFrame.grid_rowconfigure(0, weight=1)
        self.notificationLabel = ctk.CTkLabel(self.notificationFrame, text=text)
        self.notificationLabel.grid(row=0, column=0, sticky='nsew')
        self.bind("<Button-1>", lambda e: self.destroy())
        self.after(1500, self.destroy)