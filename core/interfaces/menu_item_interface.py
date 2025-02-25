from .database_interface import DatabaseInterface
from ..models import MenuItem, MenuResource
from typing import Optional
from fuzzywuzzy import fuzz
from ..database import session

class MenuItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["MenuItem"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def __is_available__(self, item: "MenuItem") -> bool:

        for resource in item.resources:
            if resource.item.inventory_item.amount < resource.amount:
                return False

        return True

    def get_items(self) -> list["MenuItem"]:
        return session.query(MenuItem).all()
    
    def get_item_by_id(self, id: int) -> Optional["MenuItem"]:
        return session.query(MenuItem).filter_by(id=id).first()
    
    def get_item_by_name(self, name: str) -> Optional["MenuItem"]:
        return session.query(MenuItem).filter_by(name=name).first()
    
    def search_item(self, query: str) -> list["MenuItem"]:

        items = []
        threshold = 80

        for item in self.items:
            if fuzz.ratio(query, item.name) >= threshold:
                items.append(item)
            elif item.name.lower().startswith(query.lower()):
                items.append(item)

        return items
    
    def get_available_items(self) -> list["MenuItem"]:

        available = []
        all_menu_items = session.query(MenuItem).all()

        for item in all_menu_items:
            if self.__is_available__(item):
                available.append(item)
            
        return available
    
    def add_item(self, name: str, cost: int, items: list["MenuResource"]) -> Optional["MenuItem"]:
        
        item = MenuItem(name, cost, items)

        if not self.__db_int__.add(item):
            return None

        self.__update_items__()

        return item
    
    def edit_name(self, item: "MenuItem", name: str) -> Optional["MenuItem"]:

        item.name = name
        
        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_cost(self, item: "MenuItem", cost: int) -> Optional["MenuItem"]:

        item.cost = cost
        
        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_resources(self, item: "MenuItem", resources: list["MenuResource"]) -> Optional["MenuItem"]:

        if len(resources) == 0:
            return None
        
        item.resources = resources
        
        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def delete_item(self, item: "MenuItem") -> Optional["MenuItem"]:

        if not self.__db_int__.delete(item):
            return None
        
        self.__update_items__()

        return item