import logging
from models.user_model import User

logging = logging.getLogger(__name__)

class UserReaderRepository:
    def __init__(self, session):
        self.db_session = session
    def get_all_users(self):
        with self.db_session as session:
            users = session.query(User).all()
            return users
        
    def get_user_by_email(self, email):
        with self.db_session as session:
            user = session.query(User).filter_by(email=email).first()
            return user
