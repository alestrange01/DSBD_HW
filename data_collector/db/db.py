from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from repositories import user_repository
import bcrypt

# if env.get("DATABASE_URL"):
#     DATABASE_URL = env.get("DATABASE_URL")
# else:
DATABASE_URL = "postgresql://root:toor@localhost:5532/postgres"


engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()



def initialize_database():
    from models.share_model import Share
    Base.metadata.create_all(engine, tables=[Share.__table__])

@contextmanager
def get_db_session():
    """Context manager per gestire automaticamente la sessione del DB."""
    session = Session()
    try:
        yield session
    finally:
        session.close()
