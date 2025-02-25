import customtkinter
from ..nav_button import nav_button


class NavFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0)

        self.app: "App" = app

        self.grid_rowconfigure(6, weight=1)

        self.home_button = nav_button(self, "Home", self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.inventory_button = nav_button(
            self, "Inventory", self.inventory_button_event)
        self.inventory_button.grid(row=2, column=0, sticky="ew")

        self.order_button = nav_button(
            self, "Order History", self.order_button_event)
        self.order_button.grid(row=3, column=0, sticky="ew")

        self.menu_button = nav_button(self, "Menu", self.menu_button_event)
        self.menu_button.grid(row=4, column=0, sticky="ew")

        self.finance_button = nav_button(
            self, "Finance", self.finance_button_event)
        self.finance_button.grid(row=5, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(
            row=8, column=0, padx=20, pady=20, sticky="s")

        self.change_appearance_mode_event("Dark")

    def select_frame_by_name(self, name):

        self.home_button.configure(
            fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.inventory_button.configure(
            fg_color=("gray75", "gray25") if name == "inventory" else "transparent")
        self.order_button.configure(
            fg_color=("gray75", "gray25") if name == "order" else "transparent")
        self.menu_button.configure(
            fg_color=("gray75", "gray25") if name == "menu" else "transparent")
        self.finance_button.configure(
            fg_color=("gray75", "gray25") if name == "finance" else "transparent")

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
        self.app.inventory.get_all_items()
        self.app.inventory.table_frame.refresh_table(
            self.app.inventory.ui_items)
        self.select_frame_by_name("inventory")

    def order_button_event(self):
        self.app.order.get_all_orders()
        self.app.order.table_frame.refresh_table(self.app.order.ui_orders)
        self.select_frame_by_name("order")

    def menu_button_event(self):
        self.select_frame_by_name("menu")

    def finance_button_event(self):
        # self.app.finance.destroy()
        # self.app.finance.grid_forget()
        # self.app.finance = FinanceFrame(self.app, self.app)
        self.app.finance.refresh_data()
        self.select_frame_by_name("finance")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
