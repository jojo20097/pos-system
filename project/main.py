from sqlalchemy import create_engine, TIMESTAMP, String, Integer, ForeignKey, Column, Table, Float
from sqlalchemy.orm import relationship, Session, DeclarativeBase, Mapped, mapped_column
from dotenv import dotenv_values
from enum import Enum
from fuzzywuzzy import fuzz
import datetime
from sqlalchemy.exc import IntegrityError
from typing import Optional, Union
import hashlib

# config = dotenv_values(".env")

# print(config["TEST"])

url = "postgresql://docker:docker@localhost:5432/systemdb"

engine = create_engine(url, echo=False)
session = Session(engine)


class Base(DeclarativeBase):
    pass


class MenuItemOrder(Base):
    __tablename__ = "menu_items_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column("menu_item_id", Integer, ForeignKey("menu_items.id"))
    order_id = Column("order_id", Integer, ForeignKey("orders.id"))
    quantity = Column(Integer)
 

class ItemMenu(Base):
    __tablename__ = "items_menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_resources_id = Column("menu_resources_id", Integer, ForeignKey("menu_resources.id"))
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
    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="item", uselist=False, cascade="all")
    menu_resources: Mapped[list["MenuResource"]] = relationship("MenuResource", cascade="all")

    def __init__(self, name: str, value_per_uom: int, uom: str) -> None:
        self.name = name
        self.value_per_uom = value_per_uom
        self.uom = uom

    def __repr__(self) -> str:
        return f"{self.name}"

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
    item: Mapped["Item"] = relationship(back_populates="menu_resources")
    
    menu_items: Mapped[list["MenuItem"]] = relationship(secondary="items_menu", back_populates="items")

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
    
    items: Mapped[list["MenuResource"]] = relationship(secondary="items_menu", back_populates="menu_items")
    order_items: Mapped[list["Order"]] = relationship(secondary="menu_items_order", back_populates="items")

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
    
    items: Mapped[list["MenuItem"]] = relationship(secondary="menu_items_order", back_populates="order_items")

    def __init__(self, value: int, items: list[MenuItem]) -> None:
        self.value = value
        self.items = items

    def __repr__(self) -> str:
        return f"({self.id}) {self.value} {self.items}"
 

Base.metadata.create_all(engine)


class DatabaseInterface:

    __ADD__ = 1
    __EDIT__ = 2
    __DELETE__ = 3

    def handle(self, object:Optional[Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]], type: int) -> bool:
        try:
            if type == self.__ADD__:
                session.add(object)
                session.commit()
            elif type == self.__EDIT__:
                session.commit()
            elif type == self.__DELETE__:
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
    
    def add(self, object: Optional[Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]]) -> bool:

        if not self.handle(object, self.__ADD__):
            return False
        
        return True
    
    def edit(self, object: Optional[Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]]) -> bool:

        if not self.handle(object, self.__EDIT__):
            return False

        return True
    
    def delete(self, object: Optional[Union[Item, User, InventoryItem, MenuResource, MenuItem, Order]]) -> bool:

        if not self.handle(object, self.__DELETE__):
            return False
    
        return True



class ItemInterface:

    items: list[Item]
    __db_int__: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[Item]:
        return session.query(Item).all()


    def add_item(self, name: str, value: int, uom: str) -> Optional[Item]:

        existing_item = session.query(Item).filter_by(name=name).all()

        if existing_item:
            return existing_item[0]

        item = Item(name, value, uom)

        if self.__db_int__.add(item):
            self.update_items()
            return item

        return None


    def edit_item(self, item: Item, name: Optional[str] = None, value: Optional[float] = None, uom: Optional[str] = None) -> bool:

        if name is None and value is None and uom is None:
            return False

        if name is not None:
            item.name = name
        if value is not None:
            item.value_per_uom = value
        if uom is not None:
            item.uom = uom
        
        if self.__db_int__.edit(item):
            self.update_items()
            return True

        return False


    def delete_item(self, item: Item) -> bool:
        
        if self.__db_int__.delete(item):
            self.update_items()
            return True

        return False


    def search_item(self, query: str) -> list[Item]:

        threshold = 80

        best_matches = [s for s in self.items if fuzz.ratio(query, s.name) >= threshold]

        for s in self.items:
            if s.name.lower().startswith(query.lower()):
                best_matches.append(s)

        return list(set(best_matches))

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        return session.query(Item).filter_by(id=item_id).first()


class UserInterface:

    user: Optional[User]
    users: list[User]
    __db_int__: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_users()

    def update_users(self) -> None:
        self.users = self.get_users()

    def get_users(self) -> list[User]:
        return session.query(User).all()

    def __make_hash__(self, plaintext: str) -> str:
        data = plaintext.encode()

        hasher = hashlib.sha256()
        hasher.update(data)
        hashed_data = hasher.digest()
        hex_digest = hashed_data.hex()

        return hex_digest

    def verify_password(self, user: User, password: str) -> bool:
        
        hash = user.password
        hex_digest = self.__make_hash__(password)

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
   
        hashed_password = self.__make_hash__(new_user_password)
        user = User(hashed_password, permissions)

        if not self.__db_int__.add(user):
            return None

        self.update_users()
        return user
    
    def create_root(self, root_password: str) -> Optional[User]:

        hashed_password = self.__make_hash__(root_password)

        root = User(hashed_password, "root")

        if not self.__db_int__.add(root):
            return None
        
        return root

    def change_password(self, target: User, old_password: str, new_password: str) -> bool:

        if self.user != target:
            return False
        
        if not self.verify_password(self.user, old_password):
            return False
        
        hashed_password = self.__make_hash__(new_password)
        target.password = hashed_password

        if not self.__db_int__.edit(target):
            return False
        
        self.update_users()
        return True
    
    def delete_user(self, target: User, user_password: str) -> Optional[User]:

        if self.user is None:
            return None

        if self.user == target:
            return None
        
        if not self.verify_password(self.user, user_password):
            return None
        
        if not self.__db_int__.delete(target):
            return None

        self.update_users()
        return target
    
    def delete_user_by_id(self, target: int, user_password: str) -> Optional[User]:

        user = session.query(User).filter(User.id == target).first()
        
        if user is None:
            return None

        return self.delete_user(user, user_password)

    
class InventoryItemInterface:

    items: list[InventoryItem]
    __db_int__: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[InventoryItem]:
        return session.query(InventoryItem).all()
    
    def add_new_item(self, name: str, value: int, uom: str, amount: int) -> Optional[InventoryItem]:

        existing_item = session.query(Item).filter_by(name=name).all()

        if existing_item:
            return None
        
        item = Item(name, value, uom)

        if self.__db_int__.add(item):
            self.update_items()
            return self.add_item(item, amount)
        
        return None

    
    def add_item(self, item: Item, amount: int) -> Optional[InventoryItem]:
        existing_item = session.query(InventoryItem).filter_by(item=item).all()

        if existing_item:
            return None
        
        inv_item = InventoryItem(amount, item)

        if self.__db_int__.add(inv_item):
            self.update_items()
            return inv_item
        
        return None
    
    def sub_amount(self, item: InventoryItem, amount: int) -> Optional[InventoryItem]:

        if amount < 0:
            return None
        
        if amount > item.amount:
            return None

        return self.edit_amount(item, item.amount - amount)

    def add_amount(self, item: InventoryItem, amount: int) -> Optional[InventoryItem]:

        if amount < 0:
            return None
        
        return self.edit_amount(item, item.amount + amount)


    def edit_amount(self, item: InventoryItem, amount: int) -> Optional[InventoryItem]:
        item.amount = amount

        if self.__db_int__.edit(item):
            self.update_items()
            return item

        return None

    def delete_item(self, item: InventoryItem) -> Optional[InventoryItem]:

        if self.__db_int__.delete(item):
            self.update_items()
            return item
        
        return None

    def search_item(self, query: str) -> list[InventoryItem]:

        threshold = 80

        best_matches = [s for s in self.items if fuzz.ratio(query, s.item.name) >= threshold]

        for s in self.items:
            if s.item.name.lower().startswith(query.lower()):
                best_matches.append(s)

        return list(set(best_matches))


class MenuResourceInterface:

    items: list[MenuResource]
    __db_int__: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[MenuResource]:
        return session.query(MenuResource).all()
    
    def add_item(self, item: Item, amount: int) -> Optional[MenuResource]:

        menu_res = MenuResource(amount, item)

        if self.__db_int__.add(menu_res):
            self.update_items()
            return menu_res

        return None

    def edit_amount(self, item: MenuResource, amount: int) -> Optional[MenuResource]:

        if amount <= 0:
            return None

        item.amount = amount

        if self.__db_int__.edit(item):
            self.update_items()
            return item

        return None

    def delete_item(self, item: MenuResource) -> Optional[MenuResource]:

        if self.__db_int__.delete(item):
            self.update_items()
            return item
        
        return None
        

class MenuItemInterface:

    items: list[MenuItem]
    __db_int__: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_items()

    def update_items(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list[MenuItem]:
        return session.query(MenuItem).all()
    
    def get_available_items(self) -> list[MenuItem]:

        result = []
        all_menu_items = session.query(MenuItem).all()

        for item in all_menu_items:
            if self.is_available(item):
                result.append(item)
            
        return result
    
    def is_available(self, item: MenuItem) -> bool:
        for resource in item.items:
            if resource.item.inventory_item.amount < resource.amount:
                return False
        return True
    
    def add_item(self, name: str, cost: int, items: list[MenuResource]) -> Optional[MenuItem]:

        existing_item = session.query(MenuItem).filter_by(name=name).all()

        if existing_item:
            return None
        
        item = MenuItem(name, cost, items)

        if self.__db_int__.add(item):
            self.update_items()
            return item
        
        return None

    def edit_item(self, item: MenuItem, name: Optional[str] = None, cost: Optional[float] = None, items: Optional[list[MenuResource]] = None) -> Optional[MenuItem]:

        if name is None and cost is None and (items is None or len(items) != 0):
            return None
        
        if name is not None:
            item.name = name
        if cost is not None:
            item.cost = cost
        if items is not None:
            item.items = items

        if self.__db_int__.edit(item):
            self.update_items()
            return item

        return None

    def delete_item(self, item: MenuItem) -> Optional[MenuItem]:

        if self.__db_int__.delete(item):
            self.update_items()
            return item
        
        return None
    
    def search_item(self, query: str) -> list[MenuItem]:

        threshold = 80

        best_matches = [s for s in self.items if fuzz.ratio(query, s.name) >= threshold]

        for s in self.items:
            if s.name.lower().startswith(query.lower()):
                best_matches.append(s)

        return list(set(best_matches))

    def get_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        return session.query(MenuItem).filter_by(id=item_id).first()

class OrderInterface:
    
    orders: list[Order]
    __db_int__: DatabaseInterface = DatabaseInterface()

    def __init__(self) -> None:
        self.update_orders()

    def update_orders(self) -> None:
        self.orders = self.get_orders()

    def get_orders(self) -> list[Order]:
        return session.query(Order).all()
    
    def can_create_order(self, items: list[MenuItem]) -> bool:
        for item in items:
            for resource in item.items:
                if resource.amount > resource.item.inventory_item.amount:
                    return False
        return True
    
    def sub_menu_resources(self, items: list[MenuItem]) -> bool:
        for item in items:
            for resource in item.items:
                resource.item.inventory_item.amount -= resource.amount
        
        if not self.__db_int__.edit(None):
            return False
        
        return True
    
    def add_menu_resources(self, items: list[MenuItem]) -> bool:
        for item in items:
                for resource in item.items:
                    resource.item.inventory_item.amount -= resource.amount
            
        if not self.__db_int__.edit(None):
            return False
            
        return True
    
    def add_order(self, value: int, items: list[MenuItem]) -> Optional[Order]:

        if len(items) == 0:
            return None
        
        if not self.can_create_order(items):
            return None
        
        order = Order(value, items)

        if not self.sub_menu_resources(items):
            return None

        if self.__db_int__.add(order):
            self.update_orders()
            return order
        
        return None
    
    def edit_order(self, order: Order, value: Optional[int] = None, items: Optional[list[MenuItem]] = None) -> Optional[Order]:

        if value is None and (items is None or len(items) != 0):
            return None
        

        if items is not None:
            if not self.add_menu_resources(order.items):
                return None
            if not self.sub_menu_resources(items):
                return None
            order.items = items
        if value is not None:
            order.value = value
        

        if self.__db_int__.edit(order):
            self.update_orders()
            return order
        
        return None
    
    def delete_order(self, order: Order) -> Optional[Order]:

        if not self.add_menu_resources(order.items):
            return None

        if self.__db_int__.delete(order):
            self.update_orders()
            return order
        
        return None


class DatabaseAPI:

    __item_int__: ItemInterface = ItemInterface()
    __user_int__: UserInterface = UserInterface()
    __inventory_item_int__: InventoryItemInterface = InventoryItemInterface()
    __menu_resource_int__: MenuResourceInterface = MenuResourceInterface()
    __menu_item_int__: MenuItemInterface = MenuItemInterface()
    __order_int__: OrderInterface = OrderInterface()

    def __valid_call__(self, *essential_permissions) -> bool:
        if self.__user_int__.user is None:
            print("Needs to login first !")
            return False
        if self.__user_int__.user.permissions not in essential_permissions:
            print("Too weak permissions !")
            return False
        return True

    # --- Basic Items API --- #

    def get_items(self) -> Optional[list[Item]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__item_int__.get_items()
    
    def add_item(self, name: str, value: int, uom: str) -> Optional[Item]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__item_int__.add_item(name, value, uom)
    
    def edit_item(self, item: Item, name: Optional[str] = None, value: Optional[int] = None) -> bool:
        if not self.__valid_call__("admin", "employee", "root"):
            return False
        return self.__item_int__.edit_item(item, name, value)
    
    def delete_item(self, item: Item) -> bool:
        if not self.__valid_call__("admin", "employee", "root"):
            return False
        return self.__item_int__.delete_item(item)
    
    def search_item(self, query: str) -> Optional[list[Item]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__item_int__.search_item(query)
    
    def get_item(self, item_id: int) -> Optional[Item]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__item_int__.get_item_by_id(item_id)
    
    # --- User API --- #

    def get_users(self) -> Optional[list[User]]:
        if not self.__valid_call__("admin", "root"):
            return None
        return self.__user_int__.get_users()
    
    def login(self, user_id: int, password: str) -> bool:
        return self.__user_int__.login(user_id, password)
    
    def logout(self) -> None:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        self.__user_int__.logout()

    def create_user(self, cur_user_password: str, new_user_password: str, permissions: str) -> Optional[User]:
        if not self.__valid_call__("admin", "root"):
            return None
        return self.__user_int__.create_user(cur_user_password, new_user_password, permissions)
    
    def create_root(self, root_password: str) -> Optional[User]:
        return self.__user_int__.create_root(root_password)
    
    def change_password(self, target: User, old_password: str, new_password: str) -> bool:
        if not self.__valid_call__("admin", "employee", "root"):
            return False
        return self.__user_int__.change_password(target, old_password, new_password)
    
    def delete_user_by_id(self, target: int, user_password: str) -> Optional[User]:
        if not self.__valid_call__("admin", "root"):
            return None
        return self.__user_int__.delete_user_by_id(target, user_password)
    
    def delete_user(self, target: User, user_password: str) -> Optional[User]:
        if not self.__valid_call__("admin", "root"):
            return None
        return self.__user_int__.delete_user(target, user_password)
    
    # --- Inventory Item API --- #

    def get_inventory_items(self) -> Optional[list[InventoryItem]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.get_items()
    
    def add_new_inventory_item(self, name: str, value: int, uom: str, amount: int) -> Optional[InventoryItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.add_new_item(name, value, uom, amount)

    def add_inventory_item(self, item: Item, amount: int) -> Optional[InventoryItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.add_item(item, amount)
    
    def sub_inventory_item_amount(self, item: InventoryItem, amount: int) -> Optional[InventoryItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.sub_amount(item, amount)
    
    def add_inventory_item_amount(self, item: InventoryItem, amount: int) -> Optional[InventoryItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.add_amount(item, amount)
    
    def delete_inventory_item(self, item: InventoryItem) -> Optional[InventoryItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.delete_item(item)
    
    def search_inventory_item(self, query: str) -> Optional[list[InventoryItem]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__inventory_item_int__.search_item(query)
    
    # --- Menu Resource API --- #

    def get_menu_resources(self) -> Optional[list[MenuResource]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_resource_int__.get_items()
    
    def add_menu_resource(self, item: Item, amount: int) -> Optional[MenuResource]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_resource_int__.add_item(item, amount)
    
    def edit_menu_resource_amount(self, item: MenuResource, amount: int) -> Optional[MenuResource]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_resource_int__.edit_amount(item, amount)
    
    def delete_menu_resource(self, item: MenuResource) -> Optional[MenuResource]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_resource_int__.delete_item(item)
    
    # --- Menu Item API --- #

    def get_menu_items(self) -> Optional[list[MenuItem]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.get_items()
    
    def get_menu_items_available(self) -> Optional[list[MenuItem]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.get_available_items()
    
    def search_menu_item(self, query: str) -> Optional[list[MenuItem]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.search_item(query)
    
    def add_menu_item(self, name: str, cost: int, items: list[MenuResource]) -> Optional[MenuItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.add_item(name, cost, items)
    
    def edit_menu_item(self, item: MenuItem, name: Optional[str] = None, cost: Optional[int] = None, items: Optional[list[MenuResource]] = None) -> Optional[MenuItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.edit_item(item, name, cost, items)
    
    def delete_menu_item(self, item: MenuItem) -> Optional[MenuItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.delete_item(item)
    
    def get_menu_item(self, item_id: int) -> Optional[MenuItem]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__menu_item_int__.get_item_by_id(item_id)
    
    # --- Order API --- #

    def get_orders(self) -> Optional[list[Order]]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__order_int__.get_orders()
    
    def add_order(self, value: int, items: list[MenuItem]) -> Optional[Order]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__order_int__.add_order(value, items)
    
    def edit_order(self, order: Order, value: Optional[int] = None, items: Optional[list[MenuItem]] = None) -> Optional[Order]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__order_int__.edit_order(order, value, items)
    
    def delete_order(self, order: Order) -> Optional[Order]:
        if not self.__valid_call__("admin", "employee", "root"):
            return None
        return self.__order_int__.delete_order(order)




handler = DatabaseAPI()

print(handler.login(1, "password"))


def database_seed() -> None:

    items = [("salt", 1, "kg"), ("sugar", 1, "kg"),
         ("water", 1, "l"), ("sunflower oil", 5, "l"),
         ("butter", 15, "kg"), ("fat", 13, "kg"),
         ("beans", 10, "kg"), ("corn", 9, "kg"),
         ("spinach", 8, "kg"), ("tomatoes", 15, "kg"),
         ("potatoes", 4, "kg"), ("bread", 3, "kg")]

    for name, value, uom in items:
        handler.add_item(name, value, uom)

    db_items = handler.get_items()

    if db_items is None:
        return

    for item in db_items:
        handler.add_inventory_item(item, 100)

    for item in db_items:
        handler.add_menu_resource(item, 20)

    resources = handler.get_menu_resources()

    if resources is None:
        return

    soup = handler.add_menu_item("soup", 10, [resources[0], resources[1]])
    pizza  = handler.add_menu_item("pizza", 20, [resources[2], resources[3], resources[4], resources[5]])

    if soup is None or pizza is None:
        return

    order1 = handler.add_order(20, [soup, pizza, pizza])

# orders = handler.get_orders()
# print(orders[0].items)

# print(orders[0].items)

# items = handler.get_items()
# for item in items:
#     handler.delete_item(item)
    