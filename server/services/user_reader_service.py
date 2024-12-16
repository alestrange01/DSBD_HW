from server.repositories import user_repository_reader

class UserReaderService: 
    def __init__(self, db_session=None):
        self.db_session = db_session #TODO Lo devo passare o la prendo qui la session come import? Io la prenderei qui

    def get_user_by_email(self, email):
        return user_repository_reader.get_user_by_email(email, self.db_session) #TODO è necessario mettere l'handler?