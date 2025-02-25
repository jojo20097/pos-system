from core import UserInterface, ItemInterface, InventoryItemInterface, MenuResourceInterface, MenuItemInterface, OrderItemInterface, OrderInterface
from core import InventoryItem, Item, MenuItem, MenuResource, OrderItem, Order, User
from typing import Optional


class DatabaseAPI:
    _instance = None

    def __new__(cls):
        # Check if an instance already exists
        if cls._instance is None:
            # Create a new instance if it doesn't exist
            cls._instance = super(DatabaseAPI, cls).__new__(cls)
            cls._instance.__initialized = False  # Track initialization
        return cls._instance

    def __init__(self):
        if not self.__initialized:
            self.user_int: UserInterface = UserInterface()
            self.__item_int__: ItemInterface = ItemInterface()
            self.__inventory_item_int__: InventoryItemInterface = InventoryItemInterface()
            self.__menu_resource_int__: MenuResourceInterface = MenuResourceInterface()
            self.__menu_item_int__: MenuItemInterface = MenuItemInterface()
            self.__order_item_int__: OrderItemInterface = OrderItemInterface()
            self.__order_int__: OrderInterface = OrderInterface()

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

    # --- Order API --- #

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

    def get_this_year_statistics(self) -> Optional[list[list[int]]]:
        '''Returns statistics for the current year'''

        if not self.__valid_call__("root", "admin", "employee"):
            return None

        return self.__order_int__.get_this_year_statistics()

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
