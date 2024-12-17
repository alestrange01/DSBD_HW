from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
import bcrypt
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

    def initialize_database(self):
        from models.user_model import User
        from models.ticker_management import TickerManagement
        from server.repositories import user_repository_reader, user_repository_writer
        from server.repositories import ticker_management_repository_writer
        self.Base.metadata.create_all(self.engine, tables=[User.__table__, TickerManagement.__table__])
        users = user_repository_reader.get_all_users()
        if not users:
            user_repository_writer.create_user("admin@gmail.com", bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "AAPL", "admin", 250.00, 220.00)
            user_repository_writer.create_user("user1@gmail.com", bcrypt.hashpw("user1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "TSLA", "user", 377.93, 327.93)
            ticker_management_repository_writer.create_ticker_management("AAPL")
            ticker_management_repository_writer.create_ticker_management("TSLA")

    @contextmanager
    def get_db_session(self):
        """Context manager per gestire automaticamente la sessione del DB."""
        session = self.Session()
        try:
            yield session
        finally:
            session.close()
