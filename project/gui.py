from typing import List
import customtkinter
import os
# from PIL import Image
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
from main import DatabaseAPI

dbAPI = DatabaseAPI()
handler = dbAPI
print(dbAPI.login("root", "root"))

def database_seed() -> None:

    items = [("salt", 1, "kg"), ("sugar", 1, "kg"),
         ("water", 1, "l"), ("sunflower oil", 5, "l"),
         ("butter", 15, "kg"), ("fat", 13, "kg"),
         ("beans", 10, "kg"), ("corn", 9, "kg"),
         ("spinach", 8, "kg"), ("tomatoes", 15, "kg"),
         ("potatoes", 4, "kg"), ("bread", 3, "kg")]

    for name, value, uom in items:
        handler.add_item(name, value, uom)

    db_items = handler.get_items()

    if db_items is None:
        return

    for item in db_items:
        handler.add_inventory_item(item, 100)

    for item in db_items:
        handler.add_menu_resource(item, 20)

    resources = handler.get_menu_resources()

    if resources is None:
        return

    soup = handler.add_menu_item("soup", 10, [resources[0], resources[1]])
    pizza  = handler.add_menu_item("pizza", 20, [resources[2], resources[3], resources[4], resources[5]])

    if soup is None or pizza is None:
        return

    soup_item = handler.add_order_item(soup, 2)
    pizza_item = handler.add_order_item(pizza, 4)

    if soup_item is None or pizza_item is None:
        return

    order1 = handler.add_order([soup_item, pizza_item])

database_seed()

# flake8: noqa

def nav_button(self, text: str, command) -> customtkinter.CTkButton:
    return customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=text,
                                    fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                    anchor="w", command=command)

class NavFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0)

        self.app: App = app

        self.grid_rowconfigure(6, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self, text="  Image Example",
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = nav_button(self, "Home", self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.inventory_button = nav_button(self, "Inventory", self.inventory_button_event)
        self.inventory_button.grid(row=2, column=0, sticky="ew")

        self.order_button = nav_button(self, "Order History", self.order_button_event)
        self.order_button.grid(row=3, column=0, sticky="ew")

        self.menu_button = nav_button(self, "Menu", self.menu_button_event)
        self.menu_button.grid(row=4, column=0, sticky="ew")

        self.finance_button = nav_button(self, "Finance", self.finance_button_event)
        self.finance_button.grid(row=5, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=8, column=0, padx=20, pady=20, sticky="s")

        self.change_appearance_mode_event("Dark")

    def select_frame_by_name(self, name):

        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.inventory_button.configure(fg_color=("gray75", "gray25") if name == "inventory" else "transparent")
        self.order_button.configure(fg_color=("gray75", "gray25") if name == "order" else "transparent")
        self.menu_button.configure(fg_color=("gray75", "gray25") if name == "menu" else "transparent")
        self.finance_button.configure(fg_color=("gray75", "gray25") if name == "finance" else "transparent")

        frame_dict = {
            "home": self.app.home,
            "inventory": self.app.inventory,
            "order": self.app.order,
            "menu": self.app.menu,
            "finance": self.app.finance,
        }

        frame_dict[name].grid(row=0, column=1, sticky="nsew")
        for key, value in frame_dict.items():
            if key != name:
                value.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def inventory_button_event(self):
        self.select_frame_by_name("inventory")

    def order_button_event(self):
        self.app.order.get_all_orders()
        self.app.order.table_frame.refresh_table(self.app.order.ui_orders)
        self.select_frame_by_name("order")

    def menu_button_event(self):
        self.select_frame_by_name("menu")

    def finance_button_event(self):
        self.select_frame_by_name("finance")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


class TableLine(customtkinter.CTkFrame):
    def __init__(self, master, app, row, values, include_modify, include_remove, include_add):
        super().__init__(master, corner_radius=0)

        self.app: App = app
        self.parent: TableFrame = master
        self.values = values
        self.elements: List[customtkinter.CTkBaseClass] = []

        button_column = len(values)

        for column, value in enumerate(values):
            column_value = customtkinter.CTkLabel(master, text=value)
            self.elements.append(column_value)
            column_value.grid(row=row, column=column, padx=10, pady=(10, 0), sticky="")
        if include_modify:
            modify_button = customtkinter.CTkButton(master, text="Modify", command=self.modify_table)
            self.elements.append(modify_button)
            modify_button.grid(row=row, column=button_column, padx=10, pady=(10, 0))
            button_column += 1
        if include_remove:
            remove_button = customtkinter.CTkButton(master, text="Remove", command=self.remove)
            self.elements.append(remove_button)
            remove_button.grid(row=row, column=button_column, padx=10, pady=(10, 0))
        if include_add:
            add_button = customtkinter.CTkButton(master, text="Add", command=self.add_item)
            self.elements.append(add_button)
            add_button.grid(row=row, column=button_column, padx=10, pady=(10, 0))
        
    def modify_table(self):
        self.parent.refresh_table([["1", "Piz", "10", "UOM", "Amount"], ["2", "Piz", "10", "UOM", "Amount"], ["3", "Piz", "10", "UOM", "Amount"], ["4", "Piz", "10", "UOM", "Amount"], ["5", "Piz", "10", "UOM", "Amount"]])

    def remove(self):
        if self.parent.column_names == ["Menu Id", "Name", "Price"]:
            menu_id = self.values[0]
            menu_item = dbAPI.get_menu_item_by_id(menu_id)
            if menu_item is None:
                popup = ErrorPopup(self, "Menu item not found")
                self.app.wait_window(popup)
                return
            res = dbAPI.delete_menu_item(menu_item)
            if res is None:
                popup = ErrorPopup(self, "Menu item deletion failed")
                self.app.wait_window(popup)
                return
            menu_frame: MenuFrame = self.parent.parent
            menu_frame.get_all_menu_items()
            self.parent.refresh_table(menu_frame.ui_items)
    
        if self.parent.column_names == ["Id", "Value", "Date"]:
            order_id = self.values[0]
            # order = dbAPI.get_order
            # dbAPI.delete_order()

        if self.parent.column_names == ["ID", "Name", "Permissions"]:
            remove_user_popup: DynamicPopup = self.parent.parent
            remove_user_popup.attributes("-topmost", False)
            user_id = self.values[0]
            entry_popup = customtkinter.CTkInputDialog(text="Password", title="User deletion auth")
            password = entry_popup.get_input()
            remove_user_popup.attributes("-topmost", False)
            usr = dbAPI.get_user_by_id(user_id)
            res = dbAPI.delete_user(usr, password)
            if res is None:
                popup = ErrorPopup(self, "Wrong password or can't delete user")
                self.app.wait_window(popup)
                return
            remove_user_popup.get_all_users()
            self.parent.refresh_table(remove_user_popup.ui_items)

    def add_item(self):
        add_popup: AddItemPopup = self.parent.parent
        add_popup.attributes("-topmost", False)
        entry_popup = customtkinter.CTkInputDialog(text="Enter amount:", title="Amount")
        try:
            amount = float(entry_popup.get_input())
        except:
            popup = ErrorPopup(self, "Wrong amount entered")
            self.app.wait_window(popup)
            return
        add_popup.attributes("-topmost", True)
        add_popup.add_item(self.values[0], amount)

class TableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, app, column_names, values, include_modify, include_remove, include_add=False, search: bool = True, inv=True):
        super().__init__(master, corner_radius=0)

        self.app: App = app
        self.parent = master
        self.column_names = column_names
        self.columns = []
        self.lines: List[TableLine] = []
        self.values = values
        self.modify = include_modify
        self.remove = include_remove
        self.add = include_add
        self.inv = inv

        self.grid_columnconfigure(len(column_names)+2, weight=1)

        self.create_table()

        if search:
            self.search = customtkinter.CTkEntry(self, width=250, placeholder_text="name...")
            self.search.grid(row=0, column=len(column_names)+2, sticky="e", padx=50)
            self.search.bind("<Return>", self.get_search_string)

    def create_table(self):
        # Create column labels
        for i, name in enumerate(self.column_names):
            label = customtkinter.CTkLabel(self, text=name, font=("", 15, "bold"))
            label.grid(row=0, column=i, padx=10, pady=(10, 0), sticky="")
            self.columns.append(label)

        # Create TableLine instances
        for row, values in enumerate(self.values):
            self.lines.append(TableLine(self, self.app, row+1, values, self.modify, self.remove, self.add))

    def refresh_table(self, new_values):
        # Clear existing lines
        for line in self.lines:
            for element in line.elements:
                element.grid_forget()
                element.destroy()
        self.lines = []
        self.values = new_values
        # Recreate TableLine instances with updated values
        for row, values in enumerate(self.values):
            line = TableLine(self, self.app, row+1, values, self.modify, self.remove, self.add)
            self.lines.append(line)

    def get_search_string(self, sequence):
        string = self.search.get()
        new_values = []
        if self.column_names == ["Item ID", "Name", "Cost", "UOM"]:
            items = dbAPI.search_item(string)
            for item in items:
                values = [item.id, item.name, item.value_per_uom, item.uom]
                new_values.append(values)
        elif self.inv:
            inv_items = dbAPI.search_item(string)
            if inv_items is not None:
                for item in inv_items:
                    values = [item.id, item.name, item.value_per_uom, item.uom, item.inventory_item.amount]
                    new_values.append(values)
        else:
            menu_items = dbAPI.search_menu_item(string)
            for item in menu_items:
                values = [item.id, item.name, item.cost]
                new_values.append(values)

        self.refresh_table(new_values)


class HomeFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_order_button = customtkinter.CTkButton(self, text="Create Order", height=60, width=200, font=("", 24), corner_radius=10, command=self.create_order)
        self.create_order_button.grid(row=1, column=1, padx=20, pady=20)
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=2, padx=20, pady=20, sticky="e")
        self.add_user_button = customtkinter.CTkButton(self, text="Add user", command=self.add_user)
        self.add_user_button.grid(row=2, column=1, pady=20, sticky="e")
        self.remove_user_button = customtkinter.CTkButton(self, text="Remove user", command=self.remove_user)
        self.remove_user_button.grid(row=2, column=2, padx=20, pady=20)

    def create_order(self):
        self.open_popup_form("order")

    def add_user(self):
        self.open_popup_form("newuser")

    def remove_user(self):
        self.open_popup_form("deleteuser")

    def open_popup_form(self, button_type):
        if button_type == "order":
            form = DynamicPopup(self.app, "Create Order", [], create_order=True)
        elif button_type == "newuser":
            form = DynamicPopup(self.app, "Create User", ["Userename:", "Permissions:", "Password:", "Your password:"])
        elif button_type == "deleteuser":
            form = DynamicPopup(self.app, "Remove User", [], remove_users=True)
        self.app.wait_window(form)
        if form.cancelled:
            return
        print(f"Order items are {form.items}")
        print(f"User to remove or add is {form.input_values}")
        if button_type == "newuser":
            username = form.input_values[0]
            permissions = form.input_values[1]
            password = form.input_values[2]
            curr_password = form.input_values[3]
            res = dbAPI.create_user(username, curr_password, password, permissions)
            if res is None:
                popup = ErrorPopup(self, "User creation failed")
                self.app.wait_window(popup)
        if button_type == "deleteuser":
            id = form.input_values[0]
            your_password = form.input_values[1]
            usr = dbAPI.get_user_by_id(id)
            res = dbAPI.delete_user(usr, your_password)
            if res is None:
                popup = ErrorPopup(self, "User deletion failed")
                self.app.wait_window(popup)
        if button_type == "order":
            new_order = dbAPI.add_order(form.items)
            print(form.total, form.items)
            if new_order is None:
                popup = ErrorPopup(self, "Order creation failed")
                self.app.wait_window(popup)


class InventoryFrame(customtkinter.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.get_all_items()

        self.table_frame = TableFrame(self, self.app, ["Id", "Name", "Price", "UOM", "Amount"], self.ui_items, True, False, False)
        self.table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Inventory", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="Add item", command=self.open_popup_form)
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e")

    def get_all_items(self) -> None:

        items = dbAPI.get_items()

        if items is None:
            popup = ErrorPopup(self, "Loading inventory failed !")
            self.app.wait_window(popup)
            return

        self.ui_items = []
        for item in items:
            values = [item.id, item.name, item.value_per_uom, item.uom, item.inventory_item.amount]
            self.ui_items.append(values)

    def open_popup_form(self):
        form = DynamicPopup(self.app, "Add Item", ["Name:", "Value:", "UOM:", "Amount:"])
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
        item = dbAPI.add_item(name, value, uom)
        if item is None:
            popup = ErrorPopup(self, "Item retrieval failed")
            self.app.wait_window(popup)
            return
        res = dbAPI.add_inventory_item(item, amount)
        if res is None:
            popup = ErrorPopup(self, "Inventory item addition failed")
            self.app.wait_window(popup)
        self.get_all_items()
        self.table_frame.refresh_table(self.ui_items)


class OrderHistoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.get_all_orders()

        self.table_frame = TableFrame(self, self.app, ["Id", "Value", "Date"], self.ui_orders, True, True, search=False)
        self.table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Order History", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="", fg_color="transparent", hover=False)
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e", )

    def get_all_orders(self):
        orders = dbAPI.get_orders()
        if orders is None:
            popup = ErrorPopup(self, "Getting orders failed")
            self.app.wait_window(popup)
            return
        self.ui_orders = []
        for item in orders:
            values = [item.id, f"{item.value:.2f} EUR", str(item.date)[:16]]
            self.ui_orders.append(values)


class MenuFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.get_all_menu_items()

        self.table_frame = TableFrame(self, self.app, ["Menu Id", "Name", "Price"], self.ui_items, False, True, search=True, inv=False)
        self.table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Menu", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="Add menu item", command=self.open_popup_form)
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e")

    def open_popup_form(self):
        form = DynamicPopup(self.app, "Add Menu Item", ["Name:", "Price:"], create_menu=True)
        self.app.wait_window(form)
        print(f"Menu ingredient items are {form.items}")
        print(f"Menu item name and price is {form.input_values}")
        name = form.input_values[0]
        price = float(form.input_values[1])
        menu_resources = [dbAPI.add_menu_resource(item, amount) for item, amount in form.items]
        if None in menu_resources:
            popup = ErrorPopup(self, "Menu resource creation failed")
            self.app.wait_window(popup)
            return
        menu_item = dbAPI.add_menu_item(name, price, menu_resources)
        if menu_item is None:
            popup = ErrorPopup(self, "Menu item creation failed")
            self.app.wait_window(popup)
            return
        self.get_all_menu_items()
        self.table_frame.refresh_table(self.ui_items)

    def get_all_menu_items(self):
        menu_items = dbAPI.get_menu_items()
        if menu_items is None:
            popup = ErrorPopup(self, "Getting menu items failed")
            self.app.wait_window(popup)
            return
        self.ui_items = []
        for item in menu_items:
            values = [item.id, item.name, item.cost]
            self.ui_items.append(values)


class FinanceFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)


        self.view_label = customtkinter.CTkLabel(self, text=f"Finance", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(0, 0), columnspan=2)
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # fig, ax = plt.subplots(facecolor='lightgrey')
        # ax.plot(["October", "November", "December", "January"], [1, 4, 2, 3])
        # ax.set_title("Monthly revenue")

        # fig2, ax2 = plt.subplots(facecolor='darkgrey')
        # ax2.bar(["October", "November", "December", "January"], [1, 4, 2, 3])
        # ax2.set_title("Monthly orders")

        # canvas = FigureCanvasTkAgg(fig, master=self)
        # canvas.draw()       
        # canvas.get_tk_widget().grid(row=1, column=0)

        # canvas2 = FigureCanvasTkAgg(fig2, master=self)
        # canvas2.draw()
        # canvas2.get_tk_widget().grid(row=1, column=1)

    
class CustomMultiInputDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title, prompts):
        super().__init__()
        self.title(title)
        self.input_values = []

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)

        # Create input fields
        self.input_entries = []
        for i, prompt in enumerate(prompts):
            label = customtkinter.CTkLabel(self, text=prompt)
            label.grid(row=i*2, column=0, padx=20, pady=0, columnspan=2)
            entry = customtkinter.CTkEntry(self)
            entry.grid(row=i*2+1, column=0, padx=20, pady=0, sticky="we", columnspan=2)
            self.input_entries.append(entry)

        # Add OK button
        ok_button = customtkinter.CTkButton(self, text="OK", command=self.get_input_values)
        ok_button.grid(row=len(prompts)+2, column=0, columnspan=2, padx=20, pady=20, sticky="we")

        password_entry: customtkinter.CTkEntry = self.input_entries[1]
        password_entry.bind("<Return>", self.get_input_values)

    def get_input_values(self, sequence=None):
        self.input_values = [entry.get() for entry in self.input_entries]
        print(self.input_values)
        self.destroy()


class DynamicPopup(customtkinter.CTkToplevel):
    def __init__(self, parent, title, prompts, create_order: bool = False, create_menu: bool = False, remove_users: bool = False):
        super().__init__(parent)
        self.attributes("-topmost", True)

        self.app: App = parent
        self.title(title)
        self.cancelled = True
        self.input_values = []
        self.items = []
        self.ui_items = []
        self.total = 0

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
            self.users_frame = TableFrame(self, self.app, ["ID", "Name", "Permissions"], self.ui_items, False, True, False, False, False)
            self.users_frame.grid(row=0, column=0, columnspan=3, sticky="nesw", padx=20, pady=20)

        # Add Confirm button
        ok_button = customtkinter.CTkButton(self, text="Confirm", command=self.get_input_values)
        ok_button.grid(row=2*len(prompts)+2, column=0, columnspan=3, padx=100 if not create_menu else 20, pady=20)

        # Add Cancel button
        cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.close)
        cancel_button.grid(row=2*len(prompts)+2, column=2, padx=20, pady=20, sticky="we")

    def get_all_users(self):
        users = dbAPI.get_users()
        if users is None:
            popup = ErrorPopup(self, "Getting users failed")
            self.app.wait_window(popup)
            return
        self.ui_items = []
        for user in users:
            values = [user.id, user.id, user.permissions]
            self.ui_items.append(values)

    def add_to_order(self):
        self.create_order_add_item("order")

    def add_to_menu(self):
        self.create_order_add_item("menu")

    def create_order_add_item(self, create_type: str):
        self.attributes("-topmost", False)
        form = AddItemPopup(self, self.app, create_type)
        self.app.wait_window(form)

        if create_type == "order":
            for id, amount in form.menu_dict.items():
                menu_item = dbAPI.get_menu_item_by_id(id)
                if menu_item is None:
                    popup = ErrorPopup(self, "Menu item fetch failed")
                    self.app.wait_window(popup)
                    return
                order_item = dbAPI.add_order_item(menu_item, amount)
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
                item = dbAPI.get_item_by_id(id)
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


class AddItemPopup(customtkinter.CTkToplevel):

    def __init__(self, parent, app, create_type):
        super().__init__(parent)
        self.attributes("-topmost", True)

        self.app: App = app
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

    def get_input_values(self, sequence=None):
        self.destroy()
        self.app.focus()

    def close(self):
        self.destroy()
        self.app.focus()

    def add_item(self, id, amount):
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


class ErrorPopup(customtkinter.CTkToplevel):
    def __init__(self, parent, error_description):
        super().__init__(parent)
        self.attributes("-topmost", True)

        self.app: App = parent
        self.title("Error occured")
        self.input_values = []

        self.geometry("400x225+1080+450")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.id_label = customtkinter.CTkLabel(self, text=error_description)
        self.id_label.grid(row=0, column=0)


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.user = dbAPI.user_int.user.username

        self.title("POS System")
        self.geometry("1920x1080+320+100")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        
    def init_frames(self):
    
        self.navigation_frame = NavFrame(master=self, app=self)

        # create home frame
        self.home = HomeFrame(master=self, app=self)

        # create inventory frame
        self.inventory = InventoryFrame(master=self, app=self)

        # create order history frame
        self.order = OrderHistoryFrame(master=self, app=self)

        # create menu frame
        self.menu = MenuFrame(master=self, app=self)

        self.finance = FinanceFrame(master=self, app=self)


if __name__ == "__main__":

    app = App()

    x_position = (app.winfo_screenwidth() - 300) // 2  # Center horizontally
    y_position = (app.winfo_screenheight() - 350) // 2  # Center vertically

    while True:
        dialog = CustomMultiInputDialog(app, "Sign In", ["Username:", "Password:"])
        dialog.geometry(f"300x200+{x_position}+{y_position}")
        app.wait_window(dialog)
        if dbAPI.login(dialog.input_values[0], dialog.input_values[1]):
            break

    app.init_frames()
    app.navigation_frame.grid(row=0, column=0, sticky="nsew")
    app.navigation_frame.select_frame_by_name("home")
    app.mainloop()
