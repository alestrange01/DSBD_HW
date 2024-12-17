from server.repositories import user_repository_reader

class UserReaderService: 
    def __init__(self, db_session):
        self.db_session = db_session #TODO Lo devo passare o la prendo qui la session come import? Io la prenderei qui
        self.user_reader_repository = user_repository_reader.UserReaderRepository(self.db_session)

    def get_user_by_email(self, email):
        return self.user_reader_repository.get_user_by_email(email, self.db_session) #TODO è necessario mettere l'handler?