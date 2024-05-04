from sqlalchemy import create_engine, TIMESTAMP, String, Integer, ForeignKey, Column, Table
from sqlalchemy.orm import relationship, Session, DeclarativeBase, Mapped, mapped_column
from dotenv import dotenv_values
from enum import Enum
from fuzzywuzzy import fuzz
import datetime
from sqlalchemy.exc import IntegrityError
from typing import Optional, Union
import hashlib

config = dotenv_values(".env")

print(config["TEST"])

url = "postgresql://docker:docker@localhost:5432/systemdb"

engine = create_engine(url, echo=True)
session = Session(engine)


class Base(DeclarativeBase):
    pass


class MenuItemOrder(Base):
    __tablename__ = "menu_items_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column("menu_item_id", Integer, ForeignKey("menu_items.id"))
    
    order_id = Column("order_id", Integer, ForeignKey("orders.id"))


class ItemMenu(Base):
    __tablename__ = "items_menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column("item_id", Integer, ForeignKey("menu_resources.id"))
    menu_id = Column("menu_id", Integer, ForeignKey("menu_items.id"))


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    password: Mapped[str] = mapped_column(String)
    permissions: Mapped[str] = mapped_column(String)

    def __init__(self, password: str, permissions: str) -> None:
        self.password = password
        self.permissions = permissions

    def __repr__(self) -> str:
        return f"User: ({self.id})"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    value_per_uom: Mapped[int] = mapped_column(Integer)
    uom: Mapped[str] = mapped_column(String)
    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="item", uselist=False)

    def __init__(self, name: str, value_per_uom: int, uom: str) -> None:
        self.name = name
        self.value_per_uom = value_per_uom
        self.uom = uom

    def __repr__(self) -> str:
        return f"Item: ({self.id})"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"))
    item: Mapped["Item"] = relationship(back_populates="inventory_item")

    def __init__(self, amount: int, item: Item) -> None:
        self.amount = amount
        self.item = item

    def __repr__(self) -> str:
        return f"{self.item.name} {self.amount}"

class MenuResource(Base):
    __tablename__ = "menu_resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"))
    item: Mapped["Item"] = relationship(back_populates="inventory_item")
    menu_items: Mapped[list["MenuItem"]] = relationship(secondary="items_menu")

    def __init__(self, amount: int, item: Item) -> None:
        self.amount = amount
        self.item = item

    def __repr__(self) -> str:
        return f"{self.item.name} {self.amount}"


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    cost: Mapped[int] = mapped_column(Integer)

    items: Mapped[list["MenuResource"]] = relationship(secondary="items_menu")
    order_items: Mapped[list["Order"]] = relationship(secondary="menu_items_order")

    def __init__(self, name: str, cost: int, items: list[MenuResource]) -> None:
        self.name = name
        self.cost = cost
        self.items = items

    def __repr__(self) -> str:
        return f"{self.name} {self.cost} {self.items}"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[int] = mapped_column(Integer)
    date: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.datetime.now())
    items: Mapped[list["MenuItem"]] = relationship(secondary="menu_items_order")

    def __init__(self, value: int, items: list[MenuItem]) -> None:
        self.value = value
        self.items = items

    def __repr__(self) -> str:
        return f"({self.id}) {self.value} {self.items}"
 

Base.metadata.create_all(engine)


class DatabaseInterface:

    ADD = 1
    EDIT = 2
    DELETE = 3

    def handle(self, object: Union[Item, User, InventoryItem, MenuResource, MenuItem, Order], type: int) -> bool:
        try:
            if type == self.ADD:
                session.add(object)
                session.commit()
            elif type == self.EDIT:
                session.commit()
            elif type == self.DELETE:
                session.delete(object)
                session.commit()

        except (IntegrityError) as e:
            session.rollback()
            print(e)
            return False
        
        except Exception as e:
            session.rollback()
            print(e)
            return False
        
        return True
    
    def add(self, object: Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]) -> bool:

        if not self.handle(object, self.ADD):
            return False
        
        return True
    
    def edit(self, object: Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]) -> bool:

        if not self.handle(object, self.EDIT):
            return False

        return True
    
    def delete(self, object: Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]) -> bool:

        if not self.handle(object, self.DELETE):
            return False
    
        return True



class ItemInterface:

    items: list[Item]
    db_int: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[Item]:
        return session.query(Item).all()


    def add_item(self, name: str, value: int, uom: str) -> bool:

        existing_item = session.query(Item).filter_by(name=name).all()

        if existing_item:
            return False
        
        item = Item(name, value, uom)

        if self.db_int.add(item):
            self.update_items()
            return True
    
        return False


    def edit_item(self, item: Item, name: Optional[str] = None, value: Optional[int] = None, uom: Optional[str] = None) -> bool:

        if name is None and value is None and uom is None:
            return False

        if name is not None:
            item.name = name
        if value is not None:
            item.value_per_uom = value
        if uom is not None:
            item.uom = uom
        
        if self.db_int.edit(item):
            self.update_items()
            return True

        return False


    def delete_item(self, item: Item) -> bool:
        
        if self.db_int.delete(item):
            self.update_items()
            return True

        return False


    def search_item(self, query: str) -> list[Item]:

        threshold = 80

        best_matches = [s for s in self.items if fuzz.ratio(query, s.name) >= threshold]

        for s in self.items:
            if s.name.lower().startswith(query.lower()):
                best_matches.append(s)

        return best_matches


class UserInterface:

    user: Optional[User]
    users: list[User]
    db_int: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_users()

    def update_users(self) -> None:
        self.users = self.get_users()

    def get_users(self) -> list[User]:
        return session.query(User).all()

    def make_hash(self, plaintext: str) -> str:
        data = plaintext.encode()

        hasher = hashlib.sha256()
        hasher.update(data)
        hashed_data = hasher.digest()
        hex_digest = hashed_data.hex()

        return hex_digest

    def verify_password(self, user: User, password: str) -> bool:
        
        hash = user.password
        hex_digest = self.make_hash(password)

        if hash != hex_digest:
            print("Invalid password !")
            return False

        return True

    def login(self, user_id: int, password: str) -> bool:
        
        user = session.query(User).filter_by(id=user_id).all()
        if not user:
            return False
        if self.verify_password(user[0], password):
            self.user = user[0]
            return True
        
        return False
    
    def logout(self) -> None:
        self.user = None
    
    def create_user(self, cur_user_password: str, new_user_password: str, permissions: str) -> Optional[User]:

        if self.user is None:
            return None

        if self.user.permissions != "admin" and self.user.permissions != "root":
            print("Weak user permissions !")
            return None
        
        if permissions not in ["admin", "employee"]:
            print("Invalid supplied permissions !")
            return None
        
        if not self.verify_password(self.user, cur_user_password):
            return None
   
        hashed_password = self.make_hash(new_user_password)
        user = User(hashed_password, permissions)

        if not self.db_int.add(user):
            return None

        self.update_users()
        return user
    
    def create_root(self, root_password: str) -> bool:

        hashed_password = self.make_hash(root_password)

        root = User(hashed_password, "root")

        if not self.db_int.add(root):
            return False
        
        return True

    def change_password(self, target: User, old_password: str, new_password: str) -> bool:

        if self.user != target:
            return False
        
        if not self.verify_password(self.user, old_password):
            return False
        
        hashed_password = self.make_hash(new_password)
        target.password = hashed_password

        if not self.db_int.edit(target):
            return False
        
        self.update_users()
        return True
    
    def delete_user(self, target: User, user_password: str) -> bool:

        if self.user is None:
            return False

        if self.user == target:
            return False
        
        if self.user.permissions not in ["admin", "root"]:
            return False
        
        if not self.verify_password(self.user, user_password):
            return False
        
        if not self.db_int.delete(target):
            return False

        self.update_users()
        return True

    
class InventoryItemInterface:

    items: list[InventoryItem]
    db_int: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[InventoryItem]:
        return session.query(InventoryItem).all()
    
    def add_item(self, item: Item, amount: int) -> bool:
        existing_item = session.query(InventoryItem).filter_by(item=item).all()

        if existing_item:
            return False
        
        inv_item = InventoryItem(amount, item)

        if self.db_int.add(inv_item):
            self.update_items()
            return True
        
        return False
    
    def sub_amount(self, item: InventoryItem, amount: int) -> bool:

        if amount < 0:
            return False
        
        if amount > item.amount:
            return False
        
        return self.edit_amount(item, item.amount - amount)

    def add_amount(self, item: InventoryItem, amount: int) -> bool:

        if amount < 0:
            return False
        
        return self.edit_amount(item, item.amount + amount)


    def edit_amount(self, item: InventoryItem, amount: int) -> bool:
        item.amount = amount

        if self.db_int.edit(item):
            self.update_items()
            return True

        return False

    def delete_item(self, item: InventoryItem) -> bool:

        if self.db_int.delete(item):
            self.update_items()
            return True
        
        return False
    
class MenuResourceInterface:

    items: list[MenuResource]
    db_int: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[MenuResource]:
        return session.query(MenuResource).all()
    
    def add_item(self, item: Item, amount: int) -> bool:
        existing_item = session.query(MenuResource).filter_by(item=item).all()

        if existing_item:
            return False
        
        inv_item = MenuResource(amount, item)

        if self.db_int.add(inv_item):
            self.update_items()
            return True
        
        return False

    def edit_amount(self, item: MenuResource, amount: int) -> bool:

        if amount <= 0:
            return False

        item.amount = amount

        if self.db_int.edit(item):
            self.update_items()
            return True

        return False

    def delete_item(self, item: MenuResource) -> bool:

        if self.db_int.delete(item):
            self.update_items()
            return True
        
        return False
        

class MenuItemInterface:

    items: list[MenuItem]
    db_int: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[MenuItem]:
        return session.query(MenuItem).all()
    
    def get_available_items(self) -> list[MenuItem]:
        return session.query(MenuItem).all()
    
    def add_item(self, name: str, cost: int, items: list[MenuResource]) -> bool:

        existing_item = session.query(MenuItem).filter_by(name=name).all()

        if existing_item:
            return False
        
        item = MenuItem(name, cost, items)

        if self.db_int.add(item):
            self.update_items()
            return True
        
        return False

    def edit_item(self, item, name: Optional[str] = None, cost: Optional[int] = None, items: Optional[list[Item]] = None) -> bool:

        if name is None and cost is None and (items is None or len(items) != 0):
            return False
        
        if name is not None:
            item.name = name
        if cost is not None:
            item.cost = cost
        if items is not None:
            item.items = items

        if self.db_int.edit(item):
            self.update_items()
            return True
        
        return False

    def delete_item(self, item: MenuItem) -> bool:

        if self.db_int.delete(item):
            self.update_items()
            return True
        
        return False
    
    def search_item(self, query: str) -> list[MenuItem]:

        threshold = 80

        best_matches = [s for s in self.items if fuzz.ratio(query, s.name) >= threshold]

        for s in self.items:
            if s.name.lower().startswith(query.lower()):
                best_matches.append(s)

        return best_matches
        

class OrderInterface:
    
    orders: list[Order]
    db_int: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_orders()

    def update_orders(self) -> None:
        self.orders = self.get_orders()

    def get_orders(self) -> list[Order]:
        return session.query(Order).all()
    
    def add_order(self, value: int, items: list[MenuItem]) -> bool:

        if len(items) == 0:
            return False
        
        order = Order(value, items)

        if self.db_int.add(order):
            self.update_orders()
            return True
        
        return False
    
    def edit_order(self, order: Order, value: int, items: list[MenuItem]) -> bool:

        if value is None and (items is None or len(items) != 0):
            return False
        
        if value is not None:
            order.value = value
        if items is not None:
            order.items = items

        if self.db_int.edit(order):
            self.update_orders()
            return True
        
        return False
    
    def delete_order(self, order: Order) -> bool:

        if self.db_int.delete(order):
            self.update_orders()
            return True
        
        return False


# item_int = ItemInterface()
# print(item_int.add_item("kofola", 1, "l"))
# print(item_int.edit_item(1, "kofolas"))
# print(item_int.items)
# print(item_int.search_item("k"))

# user_int = UserInterface()
# print(user_int.login(1, "password"))
# print(user_int.create_user("password", "1234", "admin"))
