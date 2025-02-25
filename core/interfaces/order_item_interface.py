from .database_interface import DatabaseInterface
from ..models import OrderItem, MenuItem
from typing import Optional
from ..database import session


class OrderItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["OrderItem"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list["OrderItem"]:
        return session.query(OrderItem).all()

    def get_item_by_id(self, id: int) -> Optional["OrderItem"]:
        return session.query(OrderItem).filter_by(id=id).first()

    def add_item(self, item: "MenuItem", amount: int) -> Optional["OrderItem"]:

        order_item = OrderItem(item, amount)

        if not self.__db_int__.add(order_item):
            return None

        self.__update_items__()

        return order_item

    def delete_item(self, item: "OrderItem") -> Optional["OrderItem"]:

        if not self.__db_int__.delete(item):
            return None

        self.__update_items__()

        return item
