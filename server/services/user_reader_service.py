from server.repositories import user_repository_reader
from db.db import DB

class UserReaderService: 
    def __init__(self):
        self.DB = DB()
        self.db_session = self.DB.get_db_session() #TODO Lo devo passare o la prendo qui la session come import? Io la prenderei qui
        self.user_reader_repository = user_repository_reader.UserReaderRepository(self.db_session)

    def get_user_by_email(self, email):
        return self.user_reader_repository.get_user_by_email(email) #TODO è necessario mettere l'handler?