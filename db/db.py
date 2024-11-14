from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from models import Base
from contextlib import contextmanager

# if env.get("DATABASE_URL"):
#     DATABASE_URL = env.get("DATABASE_URL")
# else:
DATABASE_URL = "postgresql+psycopg2://admin:mysecurepassword@localhost:5532/my_database"


engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

def initialize_database():
    Base.metadata.create_all(engine)

@contextmanager
def get_db_session():
    """Context manager per gestire automaticamente la sessione del DB."""
    session = Session
    try:
        yield session
    finally:
        session.close()
