import bcrypt
import logging
from db.db import DB
from repositories.user_repository_reader import UserRepositoryReader

logging = logging.getLogger(__name__)

class UserReaderService: 
    def __init__(self):
        self.db = DB()
        self.user_reader_repository = UserRepositoryReader(self.db)

    def login(self, request):
        user = self.user_reader_repository.get_user_by_email(request.email)
        if (user is None) or (not bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8'))):
            raise ValueError("Login failed: wrong email or password")
        else:
            logging.info("Login successful")
            return "Login successful", user.role
    
    def get_all_users(self):
        users = self.user_reader_repository.get_all_users()
        if users is None:
            raise ValueError("No users found")
        else:
            return users