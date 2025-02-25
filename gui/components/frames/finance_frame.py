import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class FinanceFrame(customtkinter.CTkFrame):
    MONTHS = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    def __init__(self, master, app, dbAPI):
        super().__init__(master, corner_radius=0, fg_color="transparent")

        self.app: "App" = app
        self.dbAPI = dbAPI

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.view_label = customtkinter.CTkLabel(
            self, text=f"Finance", font=("", 24, "bold"))
        self.view_label.grid(row=0, column=0, sticky="nwes",
                             padx=(0, 0), columnspan=2)
        self.signed_in_label = customtkinter.CTkLabel(
            self, text=f"Signed in as: {self.app.user}")
        self.signed_in_label.grid(
            row=0, column=2, padx=20, pady=20, sticky="e")

        self.fig, self.ax = plt.subplots(facecolor='lightgrey')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.fig2, self.ax2 = plt.subplots(facecolor='darkgrey')
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)

        self.canvas.get_tk_widget().grid(row=1, column=0)
        self.canvas2.get_tk_widget().grid(row=1, column=1)

        self.refresh_data()

    def refresh_data(self):
        finance_res = self.dbAPI.get_this_year_statistics()
        orders = [s[0] for s in finance_res]
        revenue = [s[1] for s in finance_res]

        self.ax.clear()
        self.ax.plot(self.MONTHS[:len(revenue)], revenue)
        self.ax.set_title("Monthly revenue")
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        self.ax2.clear()
        self.ax2.bar(self.MONTHS[:len(orders)], orders)
        self.ax2.set_title("Monthly orders")
        self.ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        self.canvas.draw()
        self.canvas2.draw()
