from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    item: Mapped["Item"] = relationship(back_populates="inventory_item")
    amount: Mapped[int] = mapped_column()

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    def __init__(self, item: "Item", amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> str:
        return f"({self.id}) {self.item} {self.amount}"
