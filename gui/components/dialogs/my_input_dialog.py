import customtkinter

class MyInputDialog(customtkinter.CTkInputDialog):
    def __init__(self, text, title):
        super().__init__(text=text, title=title)

        self.geometry("300x150+1130+600")
