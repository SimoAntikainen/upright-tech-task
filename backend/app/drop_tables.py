from sqlalchemy import create_engine
from .database import Base, DATABASE_URL

engine = create_engine(DATABASE_URL)

print("Dropping tables...")
Base.metadata.drop_all(bind=engine)