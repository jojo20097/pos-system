import customtkinter
from ..dialogs.error_popup import ErrorPopup
from ..dialogs.dynamic_popup import DynamicPopup

class HomeFrame(customtkinter.CTkFrame):
    def __init__(self, master, app, dbAPI):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: "App" = app
        self.dbAPI = dbAPI

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
            form = DynamicPopup(self.app, "Create Order", [], dbAPI=self.dbAPI, create_order=True)
        elif button_type == "newuser":
            form = DynamicPopup(self.app, "Create User", ["Username:", "Permissions:", "Password:", "Your password:"], dbAPI=self.dbAPI)
        elif button_type == "deleteuser":
            form = DynamicPopup(self.app, "Remove User", [], dbAPI=self.dbAPI, remove_users=True)
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
            res = self.dbAPI.create_user(username, curr_password, password, permissions)
            if res is None:
                popup = ErrorPopup(self, "User creation failed")
                self.app.wait_window(popup)
        if button_type == "deleteuser":
            id = form.input_values[0]
            your_password = form.input_values[1]
            usr = self.dbAPI.get_user_by_id(id)
            res = self.dbAPI.delete_user(usr, your_password)
            if res is None:
                popup = ErrorPopup(self, "User deletion failed")
                self.app.wait_window(popup)
        if button_type == "order":
            new_order = self.dbAPI.add_order(form.items)
            print(form.total, form.items)
            if new_order is None:
                popup = ErrorPopup(self, "Order creation failed")
                self.app.wait_window(popup)