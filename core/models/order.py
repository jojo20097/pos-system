from .base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now())

    value: Mapped[int] = mapped_column()
    items: Mapped[list["OrderItem"]] = relationship(secondary="orders_order_items", back_populates="orders")

    def __init__(self, value: int, items: list["OrderItem"]) -> None:
        self.value = value
        self.items = items

    def __repr__(self) -> str:
        return f"({self.id}) {self.value} {self.items}"
