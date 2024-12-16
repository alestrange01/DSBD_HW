import logging

from models.user_model import User

logging = logging.getLogger(__name__)

def get_all_users(db_session=None):
    with db_session as session:
        users = session.query(User).all()
        return users
    
def get_user_by_email(email, db_session=None):
    with db_session as session:
        user = session.query(User).filter_by(email=email).first()
        return user
