from sqlalchemy import Column, Integer, String

from base import Base


class Item(Base):

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value_per_uom = Column(Integer)
    uom = Column(String)

    def __init__(self, name: str, value_per_uom: int, uom: str) -> None:
        self.name = name
        self.value_per_uom = value_per_uom
        self.uom = uom

    def __repr__(self) -> None:
        return f"({self.id}) {self.name}"
    