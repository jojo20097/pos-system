from api.database_api import DatabaseAPI
from core import UserInterface

items = [("salt", 1, "kg"), ("sugar", 1, "kg"),
         ("water", 1, "l"), ("sunflower oil", 5, "l"),
         ("butter", 15, "kg"), ("fat", 13, "kg"),
         ("beans", 10, "kg"), ("corn", 9, "kg"),
         ("spinach", 8, "kg"), ("tomatoes", 15, "kg"),
         ("potatoes", 4, "kg"), ("bread", 3, "kg")
         ]


def root_user() -> None:
    user = UserInterface()
    user.create_root("root", "root")
    user.login("root", "root")


dbAPI = DatabaseAPI()
handler = dbAPI


def database_seed() -> None:

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
    pizza = handler.add_menu_item(
        "pizza", 20, [resources[2], resources[3], resources[4], resources[5]])

    if soup is None or pizza is None:
        return

    soup_item = handler.add_order_item(soup, 2)
    pizza_item = handler.add_order_item(pizza, 4)

    if soup_item is None or pizza_item is None:
        return

    handler.add_order([soup_item, pizza_item])


root_user()
print("Created root user")
database_seed()
print("Seed successfull")
