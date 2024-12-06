import logging
from db.db import get_db_session
from models.user_model import User

logging = logging.getLogger(__name__)

def get_all_users():
    with get_db_session() as session:
        users = session.query(User).all()
        return users
    
def get_user_by_email(email):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        return user
