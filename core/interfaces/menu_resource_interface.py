from .database_interface import DatabaseInterface
from ..models import MenuResource, Item
from typing import Optional
from ..database import session

class MenuResourceInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    resources: list["MenuResource"]

    def __init__(self) -> None:
        self.__update_resources__()

    def __update_resources__(self) -> None:
        self.resources = self.get_resources()

    def get_resources(self) -> list["MenuResource"]:
        return session.query(MenuResource).all()
    
    def get_resource_by_id(self, id: int) -> Optional["MenuResource"]:
        return session.query(MenuResource).filter_by(id=id).first()

    def add_item(self, item: "Item", amount: int) -> Optional["MenuResource"]:

        menu_resource = MenuResource(item, amount)

        if not self.__db_int__.add(menu_resource):
            return None
        
        self.__update_resources__()

        return menu_resource

    def delete_item(self, item: "MenuResource") -> Optional["MenuResource"]:

        if not self.__db_int__.delete(item):
            return None
        
        self.__update_resources__()
        
        return item