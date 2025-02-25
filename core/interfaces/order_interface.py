from .database_interface import DatabaseInterface
from ..models import Order, OrderItem
from typing import Optional
import datetime
from sqlalchemy import extract
from ..database import session

class OrderInterface:
    
    __db_int__: DatabaseInterface = DatabaseInterface()

    orders: list["Order"]

    def __init__(self) -> None:
        self.__update_orders__()

    def __update_orders__(self) -> None:
        self.orders = self.get_orders()

    def __sub_order_resources__(self, items: list["OrderItem"]) -> bool:

        for item in items:
            for resource in item.item.resources:
                if resource.item.inventory_item.amount < resource.amount * item.amount:
                    
                    return False

        for item in items:
            for resource in item.item.resources:
                resource.item.inventory_item.amount -= resource.amount * item.amount

        if not self.__db_int__.edit(None):
            return False

        self.__update_orders__()
        
        return True
    
    def __add_order_resources__(self, items: list["OrderItem"]) -> bool:
        
        for item in items:
            for resource in item.item.resources:
                resource.item.inventory_item.amount += resource.amount

        if not self.__db_int__.edit(None):
            return False

        self.__update_orders__()
        
        return True
    
    def __calc_order_value__(self, items: list["OrderItem"]) -> int:
        
        value = 0
        
        for item in items:
            value += item.amount * item.item.cost

        return value

    def __get_this_year_orders__(self) -> list["Order"]:
        return session.query(Order).filter(extract('year', Order.date) == datetime.datetime.now().year).all()

    def get_orders(self) -> list["Order"]:
        return session.query(Order).all()
    
    def get_order_by_id(self, id: int) -> Optional["Order"]:
        return session.query(Order).filter_by(id=id).first()
    
    def get_this_year_statistics(self) -> list[list[int]]:

        number_of_months = datetime.date.today().month

        orders = self.__get_this_year_orders__()
        monthly_revenues = [[0, 0] for _ in range(number_of_months)]

        for order in orders:
            monthly_revenues[order.date.month - 1][0] += 1
            monthly_revenues[order.date.month - 1][1] += order.value

        return monthly_revenues

    def add_order(self, items: list["OrderItem"]) -> Optional["Order"]:

        if not self.__sub_order_resources__(items):
            return None

        order = Order(self.__calc_order_value__(items), items)

        if not self.__db_int__.add(order):
            self.__add_order_resources__(items)
            return None

        self.__update_orders__()
        
        return order

    def edit_order(self, order: "Order", items: list["OrderItem"]) -> Optional["Order"]:

        if not self.__add_order_resources__(order.items):
            return None
        
        if not self.__sub_order_resources__(items):
            self.__add_order_resources__(order.items)
            return None
        
        order.value = self.__calc_order_value__(items)
        order.items = items

        if not self.__db_int__.edit(order):
            return None

        self.__update_orders__()

        return order
    
    def delete_order(self, order: "Order") -> Optional["Order"]:

        if not self.__add_order_resources__(order.items):
            return None
        
        if not self.__db_int__.delete(order):
            return None
        
        return order