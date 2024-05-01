from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from backend.objects.base import Base


engine = create_engine("postgresql:///data")


def db_created() -> bool:

    tables = inspect(engine).get_table_names()

    return len(tables) != 0


def create_db():

    if not db_created():
        Base.metadata.create_all(bind=engine)


def get_session():

    create_db()
    Session = sessionmaker(bind=engine)

    return Session()
