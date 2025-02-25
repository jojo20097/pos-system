import customtkinter
from typing import List
from api.database_api import DatabaseAPI


class TableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, app, column_names, values, include_modify, include_remove, include_add=False, search: bool = True, inv=True):
        super().__init__(master, corner_radius=0)

        self.app: "App" = app
        self.dbAPI = DatabaseAPI()

        self.parent = master
        self.column_names = column_names
        self.columns = []
        self.lines: List["TableLine"] = []
        self.values = values
        self.modify = include_modify
        self.remove = include_remove
        self.add = include_add
        self.inv = inv

        self.grid_columnconfigure(len(column_names)+2, weight=1)

        self.create_table()

        if search:
            self.search = customtkinter.CTkEntry(
                self, width=250, placeholder_text="name...")
            self.search.grid(row=0, column=len(
                column_names)+2, sticky="e", padx=50)
            self.search.bind("<Return>", self.get_search_string)

    def create_table(self):
        from ..table_line import TableLine
        # Create column labels
        for i, name in enumerate(self.column_names):
            label = customtkinter.CTkLabel(
                self, text=name, font=("", 15, "bold"))
            label.grid(row=0, column=i, padx=10, pady=(10, 0), sticky="")
            self.columns.append(label)

        # Create TableLine instances
        for row, values in enumerate(self.values):
            self.lines.append(TableLine(self, self.app, row+1, values,
                              self.modify, self.remove, self.add, dbAPI=self.dbAPI))

    def refresh_table(self, new_values):
        from ..table_line import TableLine
        # Clear existing lines
        for line in self.lines:
            for element in line.elements:
                element.grid_forget()
                element.destroy()
        self.lines = []
        self.values = new_values
        # Recreate TableLine instances with updated values
        for row, values in enumerate(self.values):
            line = TableLine(self, self.app, row+1, values,
                             self.modify, self.remove, self.add, dbAPI=self.dbAPI)
            self.lines.append(line)

    def get_search_string(self, sequence):
        string = self.search.get()
        new_values = []
        if self.column_names == ["Item ID", "Name", "Cost", "UOM"]:
            items = self.dbAPI.search_item(string)
            for item in items:
                values = [item.id, item.name, item.value_per_uom, item.uom]
                new_values.append(values)
        elif self.inv:
            inv_items = self.dbAPI.search_item(string)
            if inv_items is not None:
                for item in inv_items:
                    values = [item.id, item.name, item.value_per_uom,
                              item.uom, item.inventory_item.amount]
                    new_values.append(values)
        else:
            menu_items = self.dbAPI.search_menu_item(string)
            for item in menu_items:
                values = [item.id, item.name, item.cost]
                new_values.append(values)

        self.refresh_table(new_values)
