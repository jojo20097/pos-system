from .base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(unique=True)
    value_per_uom: Mapped[int] = mapped_column()
    uom: Mapped[str] = mapped_column()

    inventory_item: Mapped["InventoryItem"] = relationship(
        back_populates="item", uselist=False, cascade="all")
    menu_resources: Mapped[list["MenuResource"]] = relationship(cascade="all")

    def __init__(self, name: str, value_per_uom: int, uom: str) -> None:
        self.name = name
        self.value_per_uom = value_per_uom
        self.uom = uom

    def __repr__(self) -> str:
        return f"({self.id}) {self.name}"
