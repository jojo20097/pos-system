from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    item: Mapped["MenuItem"] = relationship(back_populates="order_items")
    amount: Mapped[int] = mapped_column()

    item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    orders: Mapped[list["Order"]] = relationship(secondary="orders_order_items", back_populates="items")

    def __init__(self, item: "MenuItem", amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> str:
        return f"({self.id}) {self.item} {self.amount}"
