from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from base import Base
from item import Item

from typing import List


class Menu_item(Base):

    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    cost = Column(Integer)
    items = relationship(Item, secondary='menu_item_items', backref='menu_items')

    def __init__(self, name: str, cost: int, items: List[Item]) -> None:
        self.name = name
        self.cost = cost
        self.items = items

    def __repr__(self) -> None:
        return f"({self.id}) {self.name}"
