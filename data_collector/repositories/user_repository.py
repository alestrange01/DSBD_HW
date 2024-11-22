from models.user_model import User
from db.db import get_db_session

def get_all_users():
    with get_db_session() as session:
        users = session.query(User).all()
        return users
