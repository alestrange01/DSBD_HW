import logging
from db.db import get_db_session
from models.user_model import User

logging = logging.getLogger(__name__)

def get_all_users():
    with get_db_session() as session:
        users = session.query(User).all()
        return users