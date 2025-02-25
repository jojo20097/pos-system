from .database_interface import DatabaseInterface
from ..models import User
from typing import Optional
import hashlib
from ..database import session


class UserInterface:
    _instance = None
    __db_int__: DatabaseInterface = DatabaseInterface()

    user: Optional["User"] = None
    users: list["User"]

    def __new__(cls):
        # Check if an instance already exists
        if cls._instance is None:
            # Create a new instance if it doesn't exist
            cls._instance = super(UserInterface, cls).__new__(cls)
            cls._instance.__initialized = False  # Track initialization
        return cls._instance

    def __init__(self) -> None:
        if not self.__initialized:
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
