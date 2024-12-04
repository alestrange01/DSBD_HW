from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
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

DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@postgres:{postgres_port}/{postgres_db}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

@contextmanager
def get_db_session():
    """Context manager per gestire automaticamente la sessione del DB."""
    session = Session()
    try:
        yield session
    finally:
        session.close()
