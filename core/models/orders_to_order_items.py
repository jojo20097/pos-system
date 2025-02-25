from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class OrdersToOrderItems(Base):
    __tablename__ = "orders_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
