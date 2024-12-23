from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
import os

class DB:
    Base = declarative_base()
    engine = None  
    Session = None 

    @classmethod
    def initialize(cls):
        """Inizializza l'engine e la sessione una sola volta"""
        if not cls.engine:
            postgres_user = os.getenv('POSTGRES_USER', 'root')
            postgres_password = os.getenv('POSTGRES_PASSWORD', 'toor')
            postgres_db = os.getenv('POSTGRES_DB', 'postgres')
            postgres_port = os.getenv('POSTGRES_PORT', 5532)

            cls.DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@postgres:{postgres_port}/{postgres_db}"
            cls.engine = create_engine(cls.DATABASE_URL, echo=False)
            cls.Session = sessionmaker(bind=cls.engine)

    @contextmanager
    def get_db_session(self):
        """Context manager per gestire automaticamente la sessione del DB."""
        session = self.Session()
        try:
            yield session
        finally:
            session.close()
