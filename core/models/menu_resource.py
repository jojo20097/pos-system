from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class MenuResource(Base):
    __tablename__ = "menu_resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    item: Mapped["Item"] = relationship(back_populates="menu_resources")
    amount: Mapped[int] = mapped_column()

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    menu_items: Mapped[list["MenuItem"]] = relationship(
        secondary="resources_items", back_populates="resources")

    def __init__(self, item: "Item", amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> str:
        return f"({self.id}) {self.item} {self.amount}"
