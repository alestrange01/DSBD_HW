from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
import bcrypt
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

    @classmethod
    def initialize_database(cls):
        """Crea le tabelle nel database"""
        if cls.engine is None:
            raise RuntimeError("Engine non inizializzato. Chiama DB.initialize() prima di DB.initialize_database().")

        from models.user_model import User
        from models.ticker_management import TickerManagement
        from repositories import user_repository_reader, user_repository_writer
        from repositories import ticker_management_repository_writer
        from dto.user import UserCreationDTO
        from dto.ticker_management import TickerManagementDTO
        DB.Base.metadata.create_all(cls.engine, tables=[User.__table__, TickerManagement.__table__])
        users_repo_reader = user_repository_reader.UserRepositoryReader(cls())
        users = users_repo_reader.get_all_users()
        if not users:
            user_repo_writer = user_repository_writer.UserRepositoryWriter(cls())
            admin_user = UserCreationDTO(email="admin@gmail.com", password=bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), role="admin", share_cod="AAPL", high_value=250.00, low_value=220)
            user_user = UserCreationDTO(email="user1@gmail.com", password=bcrypt.hashpw("user1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), role="user", share_cod="TSLA", high_value=377.93, low_value=327.93)
            user_repo_writer.create_user(admin_user)
            user_repo_writer.create_user(user_user)
            ticker_management_repo_writer = ticker_management_repository_writer.TickerManagementRepositoryWriter(cls())
            ticker_aapl = TickerManagementDTO("AAPL", 1)
            ticker_tsla = TickerManagementDTO("TSLA", 1)
            ticker_management_repo_writer.create_ticker_management(ticker_aapl)
            ticker_management_repo_writer.create_ticker_management(ticker_tsla)

    @contextmanager
    def get_db_session(self):
        """Context manager per gestire automaticamente la sessione del DB."""
        session = self.Session()
        try:
            yield session
        finally:
            session.close()
