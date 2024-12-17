import logging
from models.user_model import User
from dto.user import UserDTO

logging = logging.getLogger(__name__)

class UserRepositoryReader:
    def __init__(self, session):
        self.session = session
        
    def get_all_users(self):
        with self.session as session:
            users = session.query(User).all()
            users_dto = []
            for user in users:
                user_dto = UserDTO(user.email, user.share_cod, user.high_value, user.low_value)
                users_dto.append(user_dto)
            return users_dto