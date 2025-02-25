import customtkinter
from api import DatabaseAPI
from .components import NavFrame, HomeFrame, InventoryFrame, OrderHistoryFrame, MenuFrame, FinanceFrame

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.dbAPI = DatabaseAPI()
        self.user = ""

        self.title("POS System")
        self.geometry("1920x1080+320+100")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def init_frames(self, username) -> None:
        self.user = username
    
        self.navigation_frame = NavFrame(master=self, app=self)
        self.home = HomeFrame(master=self, app=self, dbAPI=self.dbAPI)
        self.inventory = InventoryFrame(master=self, app=self, dbAPI=self.dbAPI)
        self.order = OrderHistoryFrame(master=self, app=self, dbAPI=self.dbAPI)
        self.menu = MenuFrame(master=self, app=self, dbAPI=self.dbAPI)
        self.finance = FinanceFrame(master=self, app=self, dbAPI=self.dbAPI)