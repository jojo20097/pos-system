from .base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(unique=True)
    cost: Mapped[int] = mapped_column()
    resources: Mapped[list["MenuResource"]] = relationship(
        secondary="resources_items", back_populates="menu_items")

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", cascade="all")

    def __init__(self, name: str, cost: int, resources: list["MenuResource"]) -> None:
        self.name = name
        self.cost = cost
        self.resources = resources

    def __repr__(self) -> str:
        return f"({self.id}) {self.name} {self.cost} {self.resources}"
