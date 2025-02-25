import customtkinter
from ..dialogs.error_popup import ErrorPopup

from ..frames.table_frame import TableFrame

class DynamicPopup(customtkinter.CTkToplevel):
    def __init__(self, parent, title, prompts, dbAPI, create_order: bool = False, create_menu: bool = False, remove_users: bool = False):
        super().__init__(parent)
        self.attributes("-topmost", True)

        self.app: "App" = parent
        self.title(title)
        self.cancelled = True
        self.input_values = []
        self.items = []
        self.ui_items = []
        self.total = 0
        self.dbAPI = dbAPI

        # TODO: dictionary for backend functions based on title

        self.geometry("800x450+880+375")
        self.grid_columnconfigure(1, weight=1)
        if not create_menu:
            self.grid_rowconfigure(0, weight=1)
        if prompts and not create_menu:
            self.grid_rowconfigure(1+2*len(prompts), weight=1)

        # Create input fields
        self.input_entries = []
        for i, prompt in enumerate(prompts):
            label = customtkinter.CTkLabel(self, text=prompt, font=("", 14))
            label.grid(row=i*2+1, column=0, padx=100 if not create_menu else 20, pady=0 if not create_menu else (20 if i == 0 else 0, 0), columnspan=3 if not create_menu else 1)
            entry = customtkinter.CTkEntry(self, width=250)
            entry.grid(row=i*2+2, column=0, padx=100 if not create_menu else 20, pady=0 if not create_menu else 0, columnspan=3 if not create_menu else 1)
            self.input_entries.append(entry)

        if create_menu:
            self.added_items_frame = TableFrame(self, self.app, ["Name", "Amount"], [], False, False, False, False, False)
            self.added_items_frame.grid(row=5, column=0, columnspan=1, rowspan=1, sticky="nesw", padx=20, pady=20)
            self.add_item_button = customtkinter.CTkButton(self, text="Add Item", command=self.add_to_menu)
            self.add_item_button.grid(row=1, column=3, rowspan=6, padx=20)

        if create_order:
            self.added_items_frame = TableFrame(self, self.app, ["Name", "Amount", "Cost"], [], False, False, search=False)
            self.added_items_frame.grid(row=0, column=0, columnspan=2, sticky="nesw", padx=20, pady=20)
            self.add_item_button = customtkinter.CTkButton(self, text="Add Item", command=self.add_to_order)
            self.add_item_button.grid(row=0, column=2, rowspan=3)
            self.total_cost = customtkinter.CTkLabel(self, text="0.00 EUR")
            self.total_cost.grid(row=1, column=2)

        if remove_users:
            self.get_all_users()
            self.users_frame = TableFrame(self, self.app, ["ID", "Name", "Permissions"], self.ui_items, False, True, False, False, False )
            self.users_frame.grid(row=0, column=0, columnspan=3, sticky="nesw", padx=20, pady=20)

        # Add Confirm button
        ok_button = customtkinter.CTkButton(self, text="Confirm", command=self.get_input_values)
        ok_button.grid(row=2*len(prompts)+2, column=0, columnspan=3, padx=100 if not create_menu else 20, pady=20)

        # Add Cancel button
        cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.close)
        cancel_button.grid(row=2*len(prompts)+2, column=2, padx=20, pady=20, sticky="we")

    def get_all_users(self):
        users = self.dbAPI.get_users()
        if users is None:
            popup = ErrorPopup(self, "Getting users failed")
            self.app.wait_window(popup)
            return
        self.ui_items = []
        for user in users:
            values = [user.id, user.username, user.permissions]
            self.ui_items.append(values)

    def add_to_order(self):
        self.create_order_add_item("order")

    def add_to_menu(self):
        self.create_order_add_item("menu")

    def create_order_add_item(self, create_type: str):
        from ..dialogs.add_item_popup import AddItemPopup
        self.attributes("-topmost", False)
        form = AddItemPopup(self, self.app, create_type, self.dbAPI)
        self.app.wait_window(form)

        if create_type == "order":
            for id, amount in form.menu_dict.items():
                menu_item = self.dbAPI.get_menu_item_by_id(id)
                if menu_item is None:
                    popup = ErrorPopup(self, "Menu item fetch failed")
                    self.app.wait_window(popup)
                    return
                order_item = self.dbAPI.add_order_item(menu_item, amount)
                if order_item is None:
                    popup = ErrorPopup(self, "Addition of menu item failed")
                    self.app.wait_window(popup)
                    return
                
                cost = menu_item.cost * int(amount)
                format_cost = f"{cost:.2f} EUR"
                values = [menu_item.name, amount, format_cost]
                self.total += cost
                self.ui_items.append(values)
                self.items.append(order_item)
            self.refresh_total_cost_label()
        
        if create_type == "menu":
            for id, amount in form.item_dict.items():
                item = self.dbAPI.get_item_by_id(id)
                if item is None:
                    popup = ErrorPopup(self, "Item fetch failed")
                    self.app.wait_window(popup)
                    return
                values = [item.name, amount]
                self.ui_items.append(values)
                self.items.append((item, amount))

        self.added_items_frame.refresh_table(self.ui_items)
        self.attributes("-topmost", True)

    def refresh_total_cost_label(self):
        self.total_cost.configure(text=f"{self.total:.2f} EUR")

    def get_input_values(self, sequence=None):
        self.input_values = [entry.get() for entry in self.input_entries]
        self.cancelled = False
        self.destroy()
        self.app.focus()

    def close(self):
        self.destroy()
        self.app.focus()