import customtkinter

from .frames.inventory_frame import InventoryFrame
from .dialogs.error_popup import ErrorPopup
from .dialogs.my_input_dialog import MyInputDialog
from typing import List


class TableLine(customtkinter.CTkFrame):
    def __init__(self, master, app, row, values, include_modify, include_remove, include_add, dbAPI):
        super().__init__(master, corner_radius=0)

        self.app: "App" = app
        self.dbAPI = dbAPI

        from .frames.table_frame import TableFrame
        self.parent: TableFrame = master
        self.values = values
        self.elements: List[customtkinter.CTkBaseClass] = []

        button_column = len(values)

        for column, value in enumerate(values):
            column_value = customtkinter.CTkLabel(master, text=value)
            self.elements.append(column_value)
            column_value.grid(row=row, column=column,
                              padx=10, pady=(10, 0), sticky="")
        if include_modify:
            modify_button = customtkinter.CTkButton(
                master, text="Modify", command=self.modify_table)
            self.elements.append(modify_button)
            modify_button.grid(row=row, column=button_column,
                               padx=10, pady=(10, 0))
            button_column += 1
        if include_remove:
            remove_button = customtkinter.CTkButton(
                master, text="Remove", command=self.remove)
            self.elements.append(remove_button)
            remove_button.grid(row=row, column=button_column,
                               padx=10, pady=(10, 0))
        if include_add:
            add_button = customtkinter.CTkButton(
                master, text="Add", command=self.add_item)
            self.elements.append(add_button)
            add_button.grid(row=row, column=button_column,
                            padx=10, pady=(10, 0))

    def modify_table(self):
        # Modify inventory item
        if self.parent.column_names == ["Id", "Name", "Price", "UOM", "Amount"]:
            item_id = self.values[0]
            entry_popup = MyInputDialog(
                text="Enter difference:", title="Modify inventory item amount")
            try:
                difference = float(entry_popup.get_input())
            except:
                popup = ErrorPopup(self, "Wrong amount entered")
                self.app.wait_window(popup)
                return
            item = self.dbAPI.get_item_by_id(item_id)
            res = self.dbAPI.add_inventory_item_amount(item.inventory_item, int(
                difference)) if difference > 0 else self.dbAPI.sub_inventory_item_amount(item.inventory_item, -int(difference))
            if res is None:
                popup = ErrorPopup(self, "Inventory item modification failed")
                self.app.wait_window(popup)
                return
            inv_frame: InventoryFrame = self.parent.parent
            inv_frame.get_all_items()
            self.parent.refresh_table(inv_frame.ui_items)

    def remove(self):
        # Remove menu item
        if self.parent.column_names == ["Menu Id", "Name", "Price"]:
            menu_id = self.values[0]
            menu_item = self.dbAPI.get_menu_item_by_id(menu_id)
            if menu_item is None:
                popup = ErrorPopup(self, "Menu item not found")
                self.app.wait_window(popup)
                return
            res = self.dbAPI.delete_menu_item(menu_item)
            if res is None:
                popup = ErrorPopup(self, "Menu item deletion failed")
                self.app.wait_window(popup)
                return
            menu_frame: "MenuFrame" = self.parent.parent
            menu_frame.get_all_menu_items()
            self.parent.refresh_table(menu_frame.ui_items)

        if self.parent.column_names == ["Id", "Value", "Date"]:  # Remove order
            order_id = self.values[0]
            order = self.dbAPI.get_order_by_id(order_id)
            res = self.dbAPI.delete_order(order)
            if res is None:
                popup = ErrorPopup(self, "Order deletion failed")
                self.app.wait_window(popup)
                return
            order_frame: "OrderHistoryFrame" = self.parent.parent
            order_frame.get_all_orders()
            self.parent.refresh_table(order_frame.ui_orders)

        if self.parent.column_names == ["ID", "Name", "Permissions"]:  # Remove user
            remove_user_popup: "DynamicPopup" = self.parent.parent
            remove_user_popup.attributes("-topmost", False)
            user_id = self.values[0]
            entry_popup = MyInputDialog(
                text="Password", title="User deletion auth")
            password = entry_popup.get_input()
            remove_user_popup.attributes("-topmost", False)
            usr = self.dbAPI.get_user_by_id(user_id)
            res = self.dbAPI.delete_user(usr, password)
            if res is None:
                popup = ErrorPopup(self, "Wrong password or can't delete user")
                self.app.wait_window(popup)
                return
            remove_user_popup.get_all_users()
            self.parent.refresh_table(remove_user_popup.ui_items)

    def add_item(self):
        add_popup: "AddItemPopup" = self.parent.parent
        add_popup.attributes("-topmost", False)
        entry_popup = MyInputDialog(text="Enter amount:", title="Amount", )
        try:
            amount = float(entry_popup.get_input())
        except:
            popup = ErrorPopup(self, "Wrong amount entered")
            self.app.wait_window(popup)
            return
        add_popup.attributes("-topmost", True)
        add_popup.add_item(self.values[0], amount)
