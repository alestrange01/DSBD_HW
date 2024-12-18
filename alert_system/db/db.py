from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
import os

class DB:
    def __init__(self):
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

        self.DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@postgres:{postgres_port}/{postgres_db}"
        self.engine = create_engine(self.DATABASE_URL, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()

    @contextmanager
    def get_db_session(self):
        """Context manager per gestire automaticamente la sessione del DB."""
        session = self.Session()
        try:
            yield session
        finally:
            session.close()
