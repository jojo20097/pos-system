from core.database import engine, session
from core.models import *

Base.metadata.create_all(engine)
print("Successfuly created database")
