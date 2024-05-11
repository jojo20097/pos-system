from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship, Session, DeclarativeBase, Mapped, mapped_column
from typing import Optional, Union
from dotenv import dotenv_values
from fuzzywuzzy import fuzz
import datetime
import hashlib

# config = dotenv_values(".env")

# print(config["TEST"])

url = "postgresql://docker:docker@localhost:5432/systemdb"

engine = create_engine(url, echo=False)
session = Session(engine)


class Base(DeclarativeBase):
    pass


#       --- many to many table for: ---

#     OrderItem("MenuItem", "amount")
#     Order(cost, list["OrderItem"])

class OrdersToOrderItems(Base):
    __tablename__ = "orders_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
 

#       --- many to many table for: ---

#     MenuResource("Item", "amount")
#     MenuItem(cost, list["MenuResource"])

class ResourcesToItems(Base):
    __tablename__ = "resources_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    menu_resource_id: Mapped[int] = mapped_column(ForeignKey("menu_resources.id"))
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))


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


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(unique=True)
    value_per_uom: Mapped[int] = mapped_column()
    uom: Mapped[str] = mapped_column()

    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="item", uselist=False, cascade="all")
    menu_resources: Mapped[list["MenuResource"]] = relationship(cascade="all")

    def __init__(self, name: str, value_per_uom: int, uom: str) -> None:
        self.name = name
        self.value_per_uom = value_per_uom
        self.uom = uom

    def __repr__(self) -> str:
        return f"({self.id}) {self.name}"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    item: Mapped["Item"] = relationship(back_populates="inventory_item")
    amount: Mapped[int] = mapped_column()

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    def __init__(self, item: "Item", amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> str:
        return f"({self.id}) {self.item} {self.amount}"


class MenuResource(Base):
    __tablename__ = "menu_resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    item: Mapped["Item"] = relationship(back_populates="menu_resources")
    amount: Mapped[int] = mapped_column()

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    menu_items: Mapped[list["MenuItem"]] = relationship(secondary="resources_items", back_populates="resources")

    def __init__(self, item: "Item", amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> str:
        return f"({self.id}) {self.item} {self.amount}"


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(unique=True)
    cost: Mapped[int] = mapped_column()
    resources: Mapped[list["MenuResource"]] = relationship(secondary="resources_items", back_populates="menu_items")

    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", cascade="all")

    def __init__(self, name: str, cost: int, resources: list["MenuResource"]) -> None:
        self.name = name
        self.cost = cost
        self.resources = resources

    def __repr__(self) -> str:
        return f"({self.id}) {self.name} {self.cost} {self.resources}"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    item: Mapped["MenuItem"] = relationship(back_populates="order_items")
    amount: Mapped[int] = mapped_column()

    item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    orders: Mapped[list["Order"]] = relationship(secondary="orders_order_items", back_populates="items")

    def __init__(self, item: "MenuItem", amount: int) -> None:
        self.item = item
        self.amount = amount

    def __repr__(self) -> str:
        return f"({self.id}) {self.item} {self.amount}"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())

    value: Mapped[int] = mapped_column()
    items: Mapped[list["OrderItem"]] = relationship(secondary="orders_order_items", back_populates="orders")

    def __init__(self, value: int, items: list["OrderItem"]) -> None:
        self.value = value
        self.items = items

    def __repr__(self) -> str:
        return f"({self.id}) {self.value} {self.items}"

Base.metadata.create_all(engine)

class DatabaseInterface:

    __ADD__ = 1
    __EDIT__ = 2
    __DELETE__ = 3

    def handle(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]], type: int) -> bool:

        try:
            if type == self.__ADD__:
                session.add(object)
            elif type == self.__DELETE__:
                session.delete(object)
            session.commit()

        except Exception as e:
            session.rollback()
            return False
        
        return True
    
    def add(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]]) -> bool:

        if not self.handle(object, self.__ADD__):
            return False

        return True
    
    def edit(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]]) -> bool:

        if not self.handle(object, self.__EDIT__):
            return False

        return True

    def delete(self, object: Optional[Union["Item", "User", "InventoryItem", "MenuResource", "OrderItem", "MenuItem", "Order"]]) -> bool:

        if not self.handle(object, self.__DELETE__):
            return False

        return True


class UserInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    user: Optional["User"] = None
    users: list["User"]

    def __init__(self) -> None:
        self.__update_users__()

    def __update_users__(self) -> None:
        self.users = self.get_users()

    def __make_hash__(self, plaintext: str) -> str:

        hasher = hashlib.sha256()
        hasher.update(plaintext.encode())
        hashed_password = hasher.digest().hex()

        return hashed_password
    
    def __verify_password__(self, user: "User", password: str) -> bool:

        hash = self.__make_hash__(password)

        if user.password == hash:
            return True

        return False

    def get_users(self) -> list["User"]:
        return session.query(User).all()
    
    def get_user_by_id(self, id: int) -> Optional["User"]:
        return session.query(User).filter_by(id=id).first()

    def get_user_by_username(self, username: str) -> Optional["User"]:
        return session.query(User).filter_by(username=username).first()


    def login(self, username: str, password: str) -> Optional["User"]:

        user = self.get_user_by_username(username)
        
        if user is None:
            return None

        if not self.__verify_password__(user, password):
            return None

        self.user = user

        return user
    
    def logout(self) -> Optional["User"]:
        
        if self.user is None:
            return None

        user = self.user
        self.user = None

        return user
    
    def create_root(self, username: str, password: str) -> Optional["User"]:

        hashed_password = self.__make_hash__(password)
        root_user = User(username, hashed_password, "root")

        if not self.__db_int__.add(root_user):
            return None

        self.__update_users__()

        return root_user
    
    def create_user(self, username: str, current_user_password: str, new_user_password: str, permissions: str) -> Optional["User"]:

        if self.user is None:
            return None

        if not self.__verify_password__(self.user, current_user_password):
            return None

        if self.user.permissions not in ["admin", "root"]:
            return None

        if permissions not in ["admin", "employee"]:
            return None
   
        hashed_password = self.__make_hash__(new_user_password)
        new_user = User(username, hashed_password, permissions)

        if not self.__db_int__.add(new_user):
            return None

        self.__update_users__()

        return new_user

    def change_username(self, new_username: str, password: str) -> Optional["User"]:

        if self.user is None:
            return None

        if not self.__verify_password__(self.user, password):
            return None
        
        self.user.username = new_username

        if not self.__db_int__.edit(self.user):
            return None
        
        self.__update_users__()

        return self.user


    def change_password(self, old_password: str, new_password: str) -> Optional["User"]:

        if self.user is None:
            return None

        if not self.__verify_password__(self.user, old_password):
            return None

        hashed_password = self.__make_hash__(new_password)
        self.user.password = hashed_password

        if not self.__db_int__.edit(self.user):
            return None
        
        self.__update_users__()

        return self.user
    
    def delete_user(self, target: User, user_password: str) -> Optional["User"]:

        if self.user is None:
            return None

        if not self.__verify_password__(self.user, user_password):
            return None

        if self.user == target:
            return None
        
        if not self.__db_int__.delete(target):
            return None

        self.__update_users__()

        return target


class ItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["Item"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list["Item"]:
        return session.query(Item).all()
    
    def get_item_by_id(self, id: int) -> Optional["Item"]:
        return session.query(Item).filter_by(id=id).first()
    
    def get_item_by_name(self, name: str) -> Optional["Item"]:
        return session.query(Item).filter_by(name=name).first()
    
    def search_item(self, query: str) -> list["Item"]:

        items = []
        threshold = 80

        for item in self.items:
            if fuzz.ratio(query, item.name) >= threshold:
                items.append(item)
            elif item.name.lower().startswith(query.lower()):
                items.append(item)

        return items

    def add_item(self, name: str, value: int, uom: str) -> Optional["Item"]:

        item = Item(name, value, uom)

        if not self.__db_int__.add(item):
            return None

        self.__update_items__()

        return item
    
    def edit_item_name(self, item: "Item", new_name: str) -> Optional["Item"]:

        item.name = new_name

        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_item_value(self, item: "Item", new_value: int) -> Optional["Item"]:

        item.value_per_uom = new_value

        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_item_uom(self, item: "Item", new_uom: str) -> Optional["Item"]:

        item.uom = new_uom

        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def delete_item(self, item: "Item") -> Optional["Item"]:
        
        if not self.__db_int__.delete(item):
            return None

        self.__update_items__()

        return item

    
class InventoryItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["InventoryItem"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def __edit_amount__(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        item.amount = amount

        if self.__db_int__.edit(item):
            return None

        self.__update_items__()

        return item

    def get_items(self) -> list["InventoryItem"]:
        return session.query(InventoryItem).all()
    
    def get_item_by_id(self, id: int) -> Optional["InventoryItem"]:
        return session.query(InventoryItem).filter_by(id=id).first()

    def add_item(self, item: "Item", amount: int) -> Optional["InventoryItem"]:
        
        inventory_item = InventoryItem(item, amount)

        if not self.__db_int__.add(inventory_item):
            return None
        
        self.__update_items__()

        return inventory_item
    
    def add_amount(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        if amount < 0:
            return None
        
        return self.__edit_amount__(item, item.amount + amount)
    
    def sub_amount(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        if amount < 0:
            return None
        
        if amount > item.amount:
            return None

        return self.__edit_amount__(item, item.amount - amount)

    def delete_item(self, item: "InventoryItem") -> Optional["InventoryItem"]:

        if self.__db_int__.delete(item):
            return None
        
        self.__update_items__()

        return item


class MenuResourceInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    resources: list["MenuResource"]

    def __init__(self) -> None:
        self.__update_resources__()

    def __update_resources__(self) -> None:
        self.resources = self.get_resources()

    def get_resources(self) -> list["MenuResource"]:
        return session.query(MenuResource).all()
    
    def get_resource_by_id(self, id: int) -> Optional["MenuResource"]:
        return session.query(MenuResource).filter_by(id=id).first()

    def add_item(self, item: "Item", amount: int) -> Optional["MenuResource"]:

        menu_resource = MenuResource(item, amount)

        if not self.__db_int__.add(menu_resource):
            return None
        
        self.__update_resources__()

        return menu_resource

    def delete_item(self, item: "MenuResource") -> Optional["MenuResource"]:

        if not self.__db_int__.delete(item):
            return None
        
        self.__update_resources__()
        
        return item
    

class MenuItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["MenuItem"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def __is_available__(self, item: "MenuItem") -> bool:

        for resource in item.items:
            if resource.item.inventory_item.amount < resource.amount:
                return False

        return True

    def get_items(self) -> list["MenuItem"]:
        return session.query(MenuItem).all()
    
    def get_item_by_id(self, id: int) -> Optional["MenuItem"]:
        return session.query(MenuItem).filter_by(id=id).first()
    
    def get_item_by_name(self, name: str) -> Optional["MenuItem"]:
        return session.query(MenuItem).filter_by(name=name).first()
    
    def search_item(self, query: str) -> list["MenuItem"]:

        items = []
        threshold = 80

        for item in self.items:
            if fuzz.ratio(query, item.name) >= threshold:
                items.append(item)
            elif item.name.lower().startswith(query.lower()):
                items.append(item)

        return items
    
    def get_available_items(self) -> list["MenuItem"]:

        available = []
        all_menu_items = session.query(MenuItem).all()

        for item in all_menu_items:
            if self.__is_available__(item):
                available.append(item)
            
        return available
    
    def add_item(self, name: str, cost: int, items: list["MenuResource"]) -> Optional["MenuItem"]:
        
        item = MenuItem(name, cost, items)

        if not self.__db_int__.add(item):
            return None

        self.__update_items__()

        return item
    
    def edit_name(self, item: "MenuItem", name: str) -> Optional["MenuItem"]:

        item.name = name
        
        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_cost(self, item: "MenuItem", cost: int) -> Optional["MenuItem"]:

        item.cost = cost
        
        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def edit_resources(self, item: "MenuItem", resources: list["MenuResource"]) -> Optional["MenuItem"]:

        if len(resources) == 0:
            return None
        
        item.resources = resources
        
        if not self.__db_int__.edit(item):
            return None
        
        self.__update_items__()

        return item

    def delete_item(self, item: "MenuItem") -> Optional["MenuItem"]:

        if not self.__db_int__.delete(item):
            return None
        
        self.__update_items__()

        return item
    

class OrderItemInterface:

    __db_int__: DatabaseInterface = DatabaseInterface()

    items: list["OrderItem"]

    def __init__(self) -> None:
        self.__update_items__()

    def __update_items__(self) -> None:
        self.items = self.get_items()

    def get_items(self) -> list["OrderItem"]:
        return session.query(OrderItem).all()
    
    def get_item_by_id(self, id: int) -> Optional["OrderItem"]:
        return session.query(OrderItem).filter_by(id=id).first()
    
    def add_item(self, item: "MenuItem", amount: int) -> Optional["OrderItem"]:

        order_item = OrderItem(item, amount)

        if not self.__db_int__.add(order_item):
            return None
        
        self.__update_items__()
        
        return order_item
    
    def delete_item(self, item: "OrderItem") -> Optional["OrderItem"]:

        if not self.__db_int__.delete(item):
            return None
        
        self.__update_items__()

        return item


class OrderInterface:
    
    __db_int__: DatabaseInterface = DatabaseInterface()

    orders: list["Order"]

    def __init__(self) -> None:
        self.__update_orders__()

    def __update_orders__(self) -> None:
        self.orders = self.get_orders()

    def __sub_order_resources__(self, items: list["OrderItem"]) -> bool:

        for item in items:
            for resource in item.item.resources:
                resource.item.inventory_item.amount -= resource.amount

        if not self.__db_int__.edit(None):
            return False

        self.__update_orders__()
        
        return True
    
    def __add_order_resources__(self, items: list["OrderItem"]) -> bool:
        
        for item in items:
            for resource in item.item.resources:
                resource.item.inventory_item.amount += resource.amount

        if not self.__db_int__.edit(None):
            return False

        self.__update_orders__()
        
        return True
    
    def __calc_order_value__(self, items: list["OrderItem"]) -> int:
        
        value = 0
        
        for item in items:
            value += item.amount * item.item.cost

        return value


    def get_orders(self) -> list["Order"]:
        return session.query(Order).all()
    
    def get_order_by_id(self, id: int) -> Optional["Order"]:
        return session.query(Order).filter_by(id=id).first()
    
    def add_order(self, items: list["OrderItem"]) -> Optional["Order"]:

        if not self.__sub_order_resources__(items):
            return None

        order = Order(self.__calc_order_value__(items), items)

        if not self.__db_int__.add(order):
            self.__add_order_resources__(items)
            return None

        self.__update_orders__()
        
        return order

    def edit_order(self, order: "Order", items: list["OrderItem"]) -> Optional["Order"]:

        if not self.__add_order_resources__(order.items):
            return None
        
        if not self.__sub_order_resources__(items):
            self.__add_order_resources__(order.items)
            return None
        
        order.value = self.__calc_order_value__(items)
        order.items = items

        if not self.__db_int__.edit(order):
            return None

        self.__update_orders__()

        return order
    
    def delete_order(self, order: "Order") -> Optional["Order"]:

        if not self.__add_order_resources__(order.items):
            return None
        
        if not self.__db_int__.delete(order):
            return None
        
        return order


class DatabaseAPI:

    user_int: UserInterface = UserInterface()
    __item_int__: ItemInterface = ItemInterface()
    __inventory_item_int__: InventoryItemInterface = InventoryItemInterface()
    __menu_resource_int__: MenuResourceInterface = MenuResourceInterface()
    __menu_item_int__: MenuItemInterface = MenuItemInterface()
    __order_item_int__: OrderItemInterface = OrderItemInterface()
    __order_int__: OrderInterface = OrderInterface()

    def __valid_call__(self, *essential_permissions) -> bool:

        if self.user_int.user is None:
            return False
    
        if self.user_int.user.permissions not in essential_permissions:
            return False
    
        return True
    
    # --- User API --- #

    def get_users(self) -> Optional[list["User"]]:

        '''Returns list of all user objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None

        return self.user_int.get_users()
    
    def get_user_by_id(self, id: int) -> Optional["User"]:

        '''Returns user object given user id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.user_int.get_user_by_id(id)
    
    def get_user_by_username(self, username: str) -> Optional["User"]:

        '''Returns user object given username'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.user_int.get_user_by_username(username)
    
    def login(self, username: str, password: str) -> Optional["User"]:
        
        '''Logs in user given username and password'''

        return self.user_int.login(username, password)
    
    def logout(self) -> Optional["User"]:

        '''Logs out currently logged in user.'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.user_int.logout()
    
    def create_user(self, username: str, current_user_password: str, new_user_password: str, permissions: str) -> Optional["User"]:
        
        '''Creates new user given username, password and permissions.'''
        
        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.user_int.create_user(username, current_user_password, new_user_password, permissions)
    
    def change_username(self, new_username: str, password: str) -> Optional["User"]:

        '''Changes name of currently logged in user.'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.user_int.change_username(new_username, password)
    
    def change_password(self, old_password: str, new_password: str) -> Optional["User"]:

        '''Changes password of currently logged in user.'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.user_int.change_password(old_password, new_password)
    
    def delete_user(self, target: User, user_password: str) -> Optional["User"]:

        '''Deletes target user, can't delete currently logged in user.'''

        if not self.__valid_call__("root", "admin"):
            return None
        
        return self.user_int.delete_user(target, user_password)
    
    # --- Item API --- #

    def get_items(self) -> Optional[list["Item"]]:
        
        '''Returns list of all item objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.get_items()
    
    def get_item_by_id(self, id: int) -> Optional["Item"]:

        '''Returns item object given id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.get_item_by_id(id)
    
    def get_item_by_name(self, name: str) -> Optional["Item"]:

        '''Returns item object given name'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.get_item_by_name(name)
    
    def search_item(self, query: str) -> Optional[list["Item"]]:

        '''Returns list of items given query'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.search_item(query)
    
    def add_item(self, name: str, value: int, uom: str) -> Optional["Item"]:
        
        '''Creates and adds new item object to database'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.add_item(name, value, uom)

    def edit_item_name(self, item: "Item", new_name: str) -> Optional["Item"]:

        '''Edits name of the item object''' 

        if not self.__valid_call__("root", "admin", "employee"):
            return None

        return self.__item_int__.edit_item_name(item, new_name) 


    def edit_item_value(self, item: "Item", new_value: int) -> Optional["Item"]:

        '''Edits value of the item object'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.edit_item_value(item, new_value)
    
    def edit_item_uom(self, item: "Item", new_uom: str) -> Optional["Item"]:

        '''Edits uom of the item object'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.edit_item_uom(item, new_uom)
    
    def delete_item(self, item: "Item") -> Optional["Item"]:

        '''Deletes item object from the database'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__item_int__.delete_item(item)
    
    # --- Inventory Item API --- #

    def get_inventory_items(self) -> Optional[list["InventoryItem"]]:

        '''Returns list of all inventory item objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__inventory_item_int__.get_items()
    
    def get_inventory_item_by_id(self, id: int) -> Optional["InventoryItem"]:
        
        '''Returns inventory item object given id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__inventory_item_int__.get_item_by_id(id)
    
    def add_inventory_item(self, item: "Item", amount: int) -> Optional["InventoryItem"]:

        '''Creates and adds new inventory item object into databse'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__inventory_item_int__.add_item(item, amount)
    
    def add_inventory_item_amount(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:
        
        '''Adds amount to inventory item'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__inventory_item_int__.add_amount(item, amount)
    
    def sub_inventory_item_amount(self, item: "InventoryItem", amount: int) -> Optional["InventoryItem"]:

        '''Subtracts amount from inventory item'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__inventory_item_int__.sub_amount(item, amount)
    
    def delete_inventory_item(self, item: "InventoryItem") -> Optional["InventoryItem"]:

        '''Deletes inventory item from the databse'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__inventory_item_int__.delete_item(item)
    
    # --- Menu Resource API --- #

    def get_menu_resources(self) -> Optional[list["MenuResource"]]:

        '''Returns list of all menu resource objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_resource_int__.get_resources()
    
    def get_menu_resource_by_id(self, id: int) -> Optional["MenuResource"]:

        '''Returns menu resource object given id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_resource_int__.get_resource_by_id(id)
    
    def add_menu_resource(self, item: "Item", amount: int) -> Optional["MenuResource"]:

        '''Creates and adds new menu resource into databse'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_resource_int__.add_item(item, amount)
    
    def delete_menu_resource(self, item: "MenuResource") -> Optional["MenuResource"]:

        '''Delets menu resource object from database'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_resource_int__.delete_item(item)
    
    # --- Order Item API --- #

    def get_order_items(self) -> Optional[list["OrderItem"]]:

        '''Returns all order item objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_item_int__.get_items()
    
    def get_order_item_by_id(self, id: int) -> Optional["OrderItem"]:

        '''Returns order item object given id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_item_int__.get_item_by_id(id)
    
    def add_order_item(self, item: "MenuItem", amount: int) -> Optional["OrderItem"]:

        '''Creates and adds new order item into databse'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_item_int__.add_item(item, amount)
    
    def delete_order_item(self, item: "OrderItem") -> Optional["OrderItem"]:

        '''Deletes order item object from databse'''
        
        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_item_int__.delete_item(item)
    
    # --- Menu Item API --- #

    def get_menu_items(self) -> Optional[list["MenuItem"]]:

        '''Returns list of all menu item objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.get_items()
    
    def get_menu_item_by_id(self, id: int) -> Optional["MenuItem"]:

        '''Returns menu item object given id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.get_item_by_id(id)

    def get_menu_item_by_name(self, name: str) -> Optional["MenuItem"]:

        '''Returns menu item object given name'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.get_item_by_name(name)
    
    def search_menu_item(self, query: str) -> Optional[list["MenuItem"]]:

        '''Returns menu item objects given query'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.search_item(query)
    
    def get_available_menu_items(self) -> Optional[list["MenuItem"]]:

        '''Returns all available menu item objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.get_available_items()
    
    def add_menu_item(self, name: str, cost: int, items: list["MenuResource"]) -> Optional["MenuItem"]:

        '''Creates and adds new menu item object into database'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.add_item(name, cost, items)

    def edit_menu_item_name(self, item: "MenuItem", name: str) -> Optional["MenuItem"]:

        '''Edits name of menu item object'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.edit_name(item, name)
    
    def edit_menu_item_cost(self, item: "MenuItem", cost: int) -> Optional["MenuItem"]:

        '''Edits cost of menu item object'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.edit_cost(item, cost)
    
    def edit_menu_item_resources(self, item: "MenuItem", resources: list["MenuResource"]) -> Optional["MenuItem"]:

        '''Edits resources for menu item objecct'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.edit_resources(item, resources)
    
    def delete_menu_item(self, item: "MenuItem") -> Optional["MenuItem"]:

        '''Deletes menu item object from databse'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__menu_item_int__.delete_item(item)
    
    # --- Order Item API --- #

    def get_orders(self) -> Optional[list["Order"]]:

        '''Returns all order objects'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_int__.get_orders()
    
    def get_order_by_id(self, id: int) -> Optional["Order"]:

        '''Returns order object given id'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_int__.get_order_by_id(id)
    
    def add_order(self, items: list["OrderItem"]) -> Optional["Order"]:

        '''Creates and adds new order to database'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_int__.add_order(items)
    
    def edit_order(self, order: "Order", items: list["OrderItem"]) -> Optional["Order"]:    

        '''Edits items of order object'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_int__.edit_order(order, items)
    
    def delete_order(self, order: "Order") -> Optional["Order"]:

        '''Delets order object from database'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None
        
        return self.__order_int__.delete_order(order)


# Order(amount, [OrderItem(amount, MenuItem([MenuResource(amount, item)]))]

# Orders work with Order Items
# Order Items work with amounts of Menu Items
# Menu Items work with Menu Resources
# Menu Resources work with amounts of Items

# Inventory Items work with amounts of Items


handler = DatabaseAPI()

# user = UserInterface()
# user.create_root("root", "root")


print(handler.login("root", "root"))

menu_items = handler.get_menu_items()
