import customtkinter
from ..frames.table_frame import TableFrame
from ..dialogs.error_popup import ErrorPopup

class OrderHistoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, app, dbAPI):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app
        self.dbAPI = dbAPI

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.get_all_orders()

        self.table_frame = TableFrame(self, self.app, ["Id", "Value", "Date"], self.ui_orders, False, True, search=False)
        self.table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Order History", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="", fg_color="transparent", hover=False)
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e", )

    def get_all_orders(self):
        orders = self.dbAPI.get_orders()
        if orders is None:
            popup = ErrorPopup(self, "Getting orders failed")
            self.app.wait_window(popup)
            return
        self.ui_orders = []
        for item in orders:
            values = [item.id, f"{item.value:.2f} EUR", str(item.date)[:16]]
            self.ui_orders.append(values)
