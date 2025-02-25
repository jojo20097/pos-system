import customtkinter
from ..frames.table_frame import TableFrame
from ..dialogs.error_popup import ErrorPopup
from ..dialogs.dynamic_popup import DynamicPopup


class InventoryFrame(customtkinter.CTkFrame):

    def __init__(self, master, app, dbAPI):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: "App" = app
        self.dbAPI = dbAPI

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.get_all_items()

        self.table_frame = TableFrame(self, self.app, [
                                      "Id", "Name", "Price", "UOM", "Amount"], self.ui_items, True, False, False)
        self.table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(
            self, text=f"Inventory", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(
            self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(
            row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(
            self, text="Add item", command=self.open_popup_form)
        self.add_item_button.grid(
            row=2, column=1, padx=50, pady=20, sticky="e")

    def get_all_items(self) -> None:

        items = self.dbAPI.get_items()

        if items is None:
            popup = ErrorPopup(self, "Loading inventory failed !")
            self.app.wait_window(popup)
            return

        self.ui_items = []
        for item in items:
            values = [item.id, item.name, item.value_per_uom,
                      item.uom, item.inventory_item.amount]
            self.ui_items.append(values)

    def open_popup_form(self):
        form = DynamicPopup(self.app, "Add Item", [
                            "Name:", "Value:", "UOM:", "Amount:"], dbAPI=self.dbAPI)
        self.app.wait_window(form)
        if form.cancelled:
            return
        print(f"Item to add is {form.input_values}")
        try:
            name = form.input_values[0]
            value = float(form.input_values[1])
            uom = form.input_values[2]
            amount = int(form.input_values[3])
        except:
            popup = ErrorPopup(self, "Invalid item values")
            self.app.wait_window(popup)
            return
        item = self.dbAPI.add_item(name, value, uom)
        if item is None:
            popup = ErrorPopup(self, "Item retrieval failed")
            self.app.wait_window(popup)
            return
        res = self.dbAPI.add_inventory_item(item, amount)
        if res is None:
            popup = ErrorPopup(self, "Inventory item addition failed")
            self.app.wait_window(popup)
        self.get_all_items()
        self.table_frame.refresh_table(self.ui_items)
