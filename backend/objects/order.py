from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship

from base import Base
from menu_item import Menu_item

from typing import List

from datetime import datetime


class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer)
    date = Column(DateTime)
    items = relationship(Menu_item, secondary="order_items", backref="orders")

    def __init__(self, value: int, items: List[Menu_item]) -> None:
        self.date = datetime.now()
        self.value = value
        self.items = items

    def __repr__(self) -> None:
        return f"({self.id}) {self.items}"
