from .database_interface import DatabaseInterface
from ..models import InventoryItem, Item
from typing import Optional
from ..database import session

class InventoryItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["InventoryItem"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def __edit_amount__(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        item.amount = amount

        if not self.__db_int__.edit(item):
            return None

        self.__update_items__()

        return item

    def get_items(self) -> list["InventoryItem"]:
        return session.query(InventoryItem).all()
    
    def get_item_by_id(self, id: int) -> Optional["InventoryItem"]:
        return session.query(InventoryItem).filter_by(id=id).first()

    def add_item(self, item: "Item", amount: int) -> Optional["InventoryItem"]:
        
        inventory_item = InventoryItem(item, amount)

        if not self.__db_int__.add(inventory_item):
            return None
        
        self.__update_items__()

        return inventory_item
    
    def add_amount(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        if amount < 0:
            return None
        
        return self.__edit_amount__(item, item.amount + amount)
    
    def sub_amount(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        if amount < 0:
            return None
        
        if amount > item.amount:
            return None

        return self.__edit_amount__(item, item.amount - amount)

    def delete_item(self, item: "InventoryItem") -> Optional["InventoryItem"]:

        if self.__db_int__.delete(item):
            return None
        
        self.__update_items__()

        return item