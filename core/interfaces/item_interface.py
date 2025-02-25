from .database_interface import DatabaseInterface
from ..models import Item
from typing import Optional
from fuzzywuzzy import fuzz
from ..database import session

class ItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["Item"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list["Item"]:
        return session.query(Item).all()
    
    def get_item_by_id(self, id: int) -> Optional["Item"]:
        return session.query(Item).filter_by(id=id).first()
    
    def get_item_by_name(self, name: str) -> Optional["Item"]:
        return session.query(Item).filter_by(name=name).first()
    
    def search_item(self, query: str) -> list["Item"]:

        items = []
        threshold = 80

        for item in self.items:
            if fuzz.ratio(query, item.name) >= threshold:
                items.append(item)
            elif item.name.lower().startswith(query.lower()):
                items.append(item)

        return items

    def add_item(self, name: str, value: int, uom: str) -> Optional["Item"]:

        item = Item(name, value, uom)

        if not self.__db_int__.add(item):
            return None

        self.__update_items__()

        return item
    
    def edit_item_name(self, item: "Item", new_name: str) -> Optional["Item"]:

        item.name = new_name

        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_item_value(self, item: "Item", new_value: int) -> Optional["Item"]:

        item.value_per_uom = new_value

        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_item_uom(self, item: "Item", new_uom: str) -> Optional["Item"]:

        item.uom = new_uom

        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def delete_item(self, item: "Item") -> Optional["Item"]:
        
        if not self.__db_int__.delete(item):
            return None

        self.__update_items__()

        return item