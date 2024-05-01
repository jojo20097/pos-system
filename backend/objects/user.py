from sqlalchemy import Column, Integer, String

from base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String)
    permissions = Column(String)

    def __init__(self, password: str, permissions: str) -> None:
        self.password = password
        self.permissions = permissions

    def __repr__(self) -> None:
        return f"User: {self.id} / {self.permissions}"