from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class ResourcesToItems(Base):
    __tablename__ = "resources_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    menu_resource_id: Mapped[int] = mapped_column(ForeignKey("menu_resources.id"))
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
