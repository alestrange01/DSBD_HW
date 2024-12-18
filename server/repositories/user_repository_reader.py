import logging
from dto.user import UserDTO
from models.user_model import User

logging = logging.getLogger(__name__)

class UserRepositoryReader:
    def __init__(self, session):
        self.db_session = session
    def get_all_users(self):
        with self.db_session as session:
            users_dto = []
            users = session.query(User).all()
            for user in users:
                user_dto = UserDTO(email=user.email, role=user.role, share_cod=user.share_cod, high_value=user.high_value, low_value=user.low_value)
                users_dto.append(user_dto)
            return users
        
    def get_user_by_email(self, email):
        with self.db_session as session:
            user = session.query(User).filter_by(email=email).first()
            user_dto = UserDTO(email=user.email, role=user.role, share_cod=user.share_cod, high_value=user.high_value, low_value=user.low_value)
            return user_dto
        