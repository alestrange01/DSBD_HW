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
    from models.user_model import User
    Base.metadata.create_all(engine, tables=[User.__table__])
    users = user_repository.get_all_users()
    if not users:
        user_repository.create_user("admin@gmail.com", bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "AAPL")
        user_repository.create_user("user1@gmail.com", bcrypt.hashpw("user1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "TSLA")
        #user_repository.create_user("admin@gmail.com", "admin", "AAPL")
        #user_repository.create_user("user1@gmail.com", "user1", "TSLA")

@contextmanager
def get_db_session():
    """Context manager per gestire automaticamente la sessione del DB."""
    session = Session()
    try:
        yield session
    finally:
        session.close()
