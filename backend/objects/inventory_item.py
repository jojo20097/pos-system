from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from base import Base


from item import Item

class Inventory_item(Base):

    __tablename__ = "inventory_item"

    item = relationship(Item, backref="inventory_items")
    amount = Column(Integer)

    def __init__(self, item: Item, amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> None:
        return f"{self.item} {self.amount}"
