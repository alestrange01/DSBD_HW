from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from repositories import user_repository
import os

if os.getenv('POSTGRES_USER'):
    postgres_user = os.getenv('POSTGRES_USER')
else:
    postgres_user = "root"
if os.getenv('POSTGRES_PASSWORD'):
    postgres_password = os.getenv('POSTGRES_PASSWORD')
else:
    postgres_password = "toor"
if os.getenv('POSTGRES_DB'):
    postgres_db = os.getenv('POSTGRES_DB')
else:
    postgres_db = "postgres"
if os.getenv('POSTGRES_PORT'):
    postgres_port = os.getenv('POSTGRES_PORT')
else:
    postgres_port = 5532

DATABASE_URL = "postgresql://" + postgres_user + ":" + postgres_password + "@localhost:" + str(postgres_port) + "/" + postgres_db


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
