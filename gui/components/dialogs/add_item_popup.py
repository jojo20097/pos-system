import customtkinter

from ..frames.table_frame import TableFrame

class AddItemPopup(customtkinter.CTkToplevel):

    def __init__(self, parent: customtkinter.CTkToplevel, app: "App", create_type: str, dbAPI) -> None:
        super().__init__(parent)

        self.attributes("-topmost", True)

        self.app: "App" = app
        self.dbAPI = dbAPI
        self.title("Add menu item")
        self.type = create_type
        self.menu_dict = {}
        self.item_dict = {}

        self.geometry("800x450+880+375")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        if create_type == "menu":
            items = dbAPI.get_items()
            if items is None:
                from ..dialogs.error_popup import ErrorPopup
                popup = ErrorPopup(self, "Getting items failed")
                self.app.wait_window(popup)
                return
            ui_items = []
            for item in items:
                values = [item.id, item.name, item.value_per_uom, item.uom]
                ui_items.append(values)
            self.menu_table_frame = TableFrame(self, self.app, ["Item ID", "Name", "Cost", "UOM"], ui_items, False, False, True, True, False)
            self.menu_table_frame.grid(row=0, column=0, columnspan=3, rowspan=6, padx=20, pady=20, sticky="nswe")

        if create_type == "order":
            self.app.menu.get_all_menu_items()
            self.menu_table_frame = TableFrame(self, self.app, ["Menu Id", "Name", "Price"], self.app.menu.ui_items, False, False, True, True, False)
            self.menu_table_frame.grid(row=0, column=0, columnspan=3, rowspan=6, padx=20, pady=20, sticky="nswe")

        # Add Confirm button
        ok_button = customtkinter.CTkButton(self, text="Confirm", command=self.get_input_values)
        ok_button.grid(row=6, column=0, columnspan=1, padx=20, pady=20)

        # Add Cancel button
        cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.close)
        cancel_button.grid(row=6, column=2, padx=20, pady=20, sticky="we")

    def get_input_values(self) -> None:
        self.destroy()
        self.app.focus()

    def close(self) -> None:
        self.destroy()
        self.app.focus()

    def add_item(self, id, amount) -> None:

        if self.type == "menu":
            if id not in self.item_dict:
                self.item_dict[id] = amount
            else:
                self.item_dict[id] += amount

        if self.type == "order":
            if id not in self.item_dict:
                self.menu_dict[id] = amount
            else:
                self.menu_dict[id] += amount