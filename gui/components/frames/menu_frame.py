import customtkinter
from ..frames.table_frame import TableFrame
from ..dialogs.dynamic_popup import DynamicPopup
from ..dialogs.error_popup import ErrorPopup


class MenuFrame(customtkinter.CTkFrame):
    def __init__(self, master, app, dbAPI):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: "App" = app
        self.dbAPI = dbAPI

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.get_all_menu_items()

        self.table_frame = TableFrame(self, self.app, [
                                      "Menu Id", "Name", "Price"], self.ui_items, False, True, search=True, inv=False)
        self.table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(
            self, text=f"Menu", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(
            self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(
            row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(
            self, text="Add menu item", command=self.open_popup_form)
        self.add_item_button.grid(
            row=2, column=1, padx=50, pady=20, sticky="e")

    def open_popup_form(self):
        form = DynamicPopup(self.app, "Add Menu Item", [
                            "Name:", "Price:"], dbAPI=self.dbAPI, create_menu=True)
        self.app.wait_window(form)
        print(f"Menu ingredient items are {form.items}")
        print(f"Menu item name and price is {form.input_values}")
        name = form.input_values[0]
        price = float(form.input_values[1])
        menu_resources = [self.dbAPI.add_menu_resource(
            item, amount) for item, amount in form.items]
        if None in menu_resources:
            popup = ErrorPopup(self, "Menu resource creation failed")
            self.app.wait_window(popup)
            return
        menu_item = self.dbAPI.add_menu_item(name, price, menu_resources)
        if menu_item is None:
            popup = ErrorPopup(self, "Menu item creation failed")
            self.app.wait_window(popup)
            return
        self.get_all_menu_items()
        self.table_frame.refresh_table(self.ui_items)

    def get_all_menu_items(self):
        menu_items = self.dbAPI.get_menu_items()
        if menu_items is None:
            popup = ErrorPopup(self, "Getting menu items failed")
            self.app.wait_window(popup)
            return
        self.ui_items = []
        for item in menu_items:
            values = [item.id, item.name, item.cost]
            self.ui_items.append(values)
