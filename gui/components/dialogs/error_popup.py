import customtkinter


class ErrorPopup(customtkinter.CTkToplevel):

    def __init__(self, parent: customtkinter.CTkFrame, error_description: str) -> None:
        super().__init__(parent)

        self.attributes("-topmost", True)

        self.app: "App" = parent
        self.title("Error")

        self.geometry("400x225+1080+525")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.id_label = customtkinter.CTkLabel(self, text=error_description)
        self.id_label.grid(row=0, column=0)
