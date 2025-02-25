from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import dotenv_values

config = dotenv_values(".env")
url = config["url"]

engine = create_engine(url)
session = Session(bind=engine)
