import customtkinter
import os
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# flake8: noqa


class NavFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0)

        self.app: App = app

        self.grid_rowconfigure(6, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self, text="  Image Example",
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.inventory_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Inventory",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.inventory_button_event)
        self.inventory_button.grid(row=2, column=0, sticky="ew")

        self.order_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Order History",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.order_button_event)
        self.order_button.grid(row=3, column=0, sticky="ew")

        self.menu_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Menu",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.menu_button_event)
        self.menu_button.grid(row=4, column=0, sticky="ew")

        self.finance_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Finance",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.finance_button_event)
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
        self.select_frame_by_name("order")

    def menu_button_event(self):
        self.select_frame_by_name("menu")

    def finance_button_event(self):
        self.select_frame_by_name("finance")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)



class TableLine(customtkinter.CTkFrame):
    def __init__(self, master, app, row, values, include_modify, include_remove, color):
        super().__init__(master, corner_radius=0, fg_color=color)

        self.app: App = app
        self.values = values

        button_column = len(values)

        for column, value in enumerate(values):
            column_value = customtkinter.CTkLabel(master, text=value)
            column_value.grid(row=row, column=column, padx=10, pady=(10, 0), sticky="")
        if include_modify:
            modify_button = customtkinter.CTkButton(master, text="Modify")
            modify_button.grid(row=row, column=button_column, padx=10, pady=(10, 0))
            button_column += 1
        if include_remove:
            remove_button = customtkinter.CTkButton(master, text="Remove")
            remove_button.grid(row=row, column=button_column, padx=10, pady=(10, 0))

    
class TableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, app, column_names, values, include_modify, include_remove):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app
        self.column_names = column_names
        self.columns = []
        self.lines = []
        self.values = values

        self.grid_columnconfigure(len(column_names)+2, weight=1)

        # TODO: Call correct method to get data to display

        for i, name in enumerate(self.column_names):
            label = customtkinter.CTkLabel(self, text=name, font=("", 15, "bold"))
            label.grid(row=0, column=i, padx=10, pady=(10, 0), sticky="")
            self.columns.append(label)

        for row, values in enumerate(self.values):
            line = TableLine(self, self.app, row+1, values, include_modify, include_remove, "grey70" if row % 2 == 0 else "grey90")
            self.lines.append(line)
        
        self.search = customtkinter.CTkEntry(self, width=250, placeholder_text="item name...")
        self.search.grid(row=0, column=len(column_names)+2, sticky="e", padx=50)
        self.search.bind("<Return>", self.get_search_string)

    def get_search_string(self, sequence):
        string = self.search.get()
        print(string)


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
            form = DynamicPopup(self.app, "Create Order", [])
        elif button_type == "newuser":
            form = DynamicPopup(self.app, "Create User", ["ID:", "Password:"])
        elif button_type == "deleteuser":
            form = DynamicPopup(self.app, "Remove User", ["ID:", "Password:"])
        self.app.wait_window(form)


class InventoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.inventory_table_frame = TableFrame(self, self.app, ["Id", "Name", "Price", "UOM", "Amount"], [["1", "Pizza", "10", "UOM", "Amount"], ["1", "Pizza", "10", "UOM", "Amount"], ["1", "Pizza", "10", "UOM", "Amount"], ["1", "Pizza", "10", "UOM", "Amount"], ["1", "Pizza", "10", "UOM", "Amount"]], True, False)
        self.inventory_table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Inventory", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="Add item")
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e")

    def open_popup_form(self):
        form = DynamicPopup(self.app)
        self.app.wait_window(form)


class OrderHistoryFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.inventory_table_frame = TableFrame(self, self.app, ["Id", "Value", "Date"], [["1", "1337", "1/2/3"], ["1", "1337", "1/2/3"], ["1", "1337", "1/2/3"], ["1", "1337", "1/2/3"], ["1", "1337", "1/2/3"]], True, True)
        self.inventory_table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Order History", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="", fg_color="transparent", hover=False)
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e", )


class MenuFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: App = app

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.inventory_table_frame = TableFrame(self, self.app, ["Menu Id", "Name", "Price"], [["1", "Pizza", "10"], ["1", "Pizza", "10"], ["1", "Pizza", "10"], ["1", "Pizza", "10"], ["1", "Pizza", "10"]], False, True)
        self.inventory_table_frame.grid(row=1, column=0, sticky="nwes", padx=50, pady=0)

        self.view_label = customtkinter.CTkLabel(self, text=f"Menu", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes", padx=(150, 0))
        self.signed_in_label = customtkinter.CTkLabel(self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        self.add_item_button = customtkinter.CTkButton(self, text="Add menu item")
        self.add_item_button.grid(row=2, column=1, padx=50, pady=20, sticky="e")

    def open_popup_form(self):
        form = DynamicPopup(self.app)
        self.app.wait_window(form)


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

        fig, ax = plt.subplots(facecolor='lightgrey')
        ax.plot(["October", "November", "December", "January"], [1, 4, 2, 3])
        ax.set_title("Monthly revenue")

        fig2, ax2 = plt.subplots(facecolor='darkgrey')
        ax2.bar(["October", "November", "December", "January"], [1, 4, 2, 3])
        ax2.set_title("Monthly orders")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()       
        canvas.get_tk_widget().grid(row=1, column=0)

        canvas2 = FigureCanvasTkAgg(fig2, master=self)
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=1, column=1)

    
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
    def __init__(self, parent, title, prompts):
        super().__init__(parent)

        self.app: App = parent
        self.title(title)
        self.input_values = []

        self.geometry("1200x675+680+300")
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
        ok_button = customtkinter.CTkButton(self, text="Confirm", command=self.get_input_values)
        ok_button.grid(row=len(prompts)+2, column=0, columnspan=2, padx=20, pady=20, sticky="we")

        cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.close)
        cancel_button.grid(row=len(prompts)+2, column=2, padx=20, pady=20, sticky="we")

        # password_entry: customtkinter.CTkEntry = self.input_entries[1]
        # password_entry.bind("<Return>", self.get_input_values)

    def get_input_values(self, sequence=None):
        self.input_values = [entry.get() for entry in self.input_entries]
        print(self.input_values)
        self.destroy()
        self.app.focus()


    def close(self):
        self.destroy()
        self.app.focus()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.user = "Admin"

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
    auth = False
    while not auth:
        dialog = CustomMultiInputDialog(app, "Sign In", ["ID:", "Password:"])
        dialog.geometry(f"300x200+{x_position}+{y_position}")
        app.wait_window(dialog)
        if dialog.input_values == ['13', 'panbohprinas']:
            app.user = dialog.input_values[0]
            print(app.user)
            auth = True
    app.init_frames()
    app.navigation_frame.grid(row=0, column=0, sticky="nsew")
    app.navigation_frame.select_frame_by_name("home")
    app.mainloop()
