import customtkinter as ctk

class FloatingMenu(ctk.CTkToplevel):
    def __init__(self, width, height, x=0, y=0):
        super().__init__()
        self.overrideredirect(True)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.wm_attributes('-transparentcolor','#FFFFFF')
        self.config(bg='#FFFFFF')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.after(50, self.focus_set)
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<FocusOut>", lambda event: self.destroy())