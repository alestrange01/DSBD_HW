import logging
from dto.user import UserDTO
from models.user_model import User

logging = logging.getLogger(__name__)

class UserRepositoryReader:
    def __init__(self, db):
        self.db = db
        
    def get_all_users(self):
        with self.db.get_db_session() as session:
            users = session.query(User).all()
            users_dto = []
            for user in users:
                user_dto = UserDTO(user.email, user.share_cod, user.high_value, user.low_value)
                users_dto.append(user_dto)
            return users_dto