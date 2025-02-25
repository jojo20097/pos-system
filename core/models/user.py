# core/models/user.py
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    permissions: Mapped[str] = mapped_column()

    def __init__(self, username: str, password: str, permissions: str) -> None:
        self.username = username
        self.password = password
        self.permissions = permissions

    def __repr__(self) -> str:
        return f"({self.id}) {self.username} ({self.permissions})"
