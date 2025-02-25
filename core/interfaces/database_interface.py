from ..models import Item, User, InventoryItem, MenuResource, OrderItem, MenuItem, Order
from typing import Optional, Union
from ..database import session

class DatabaseInterface:

    __ADD__ = 1
    __EDIT__ = 2
    __DELETE__ = 3

    def handle(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]], type: int) -> bool:

        try:
            if type == self.__ADD__:
                session.add(object)
            elif type == self.__DELETE__:
                session.delete(object)
            session.commit()

        except Exception as e:
            session.rollback()
            return False
        
        return True
    
    def add(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]]) -> bool:

        if not self.handle(object, self.__ADD__):
            return False

        return True
    
    def edit(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]]) -> bool:

        if not self.handle(object, self.__EDIT__):
            return False

        return True

    def delete(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]]) -> bool:

        if not self.handle(object, self.__DELETE__):
            return False

        return True