import logging
from db.db import DB
from server.repositories.share_repository_reader import ShareRepositoryReader
from server.repositories.user_repository_reader import UserRepositoryReader

logging = logging.getLogger(__name__)

class ShareReaderService: 
    def __init__(self):
        self.DB = DB()
        self.db_session = self.DB.get_db_session()
        self.share_repository_reader = ShareRepositoryReader(self.db_session)
        self.user_repository_reader = UserRepositoryReader(self.db_session)
        
    def get_all_shares(self):
        shares = self.share_repository_reader.get_all_shares()
        if shares is None:
            raise ValueError("Retrieve all shares failed")
        else:
           return shares

    def get_values_share(self, user_email):
            user = self.user_repository_reader.get_user_by_email(user_email)
            share_name = user.share_cod
            share = self.share_repository_reader.get_latest_share_by_name(share_name)
            if share is None:
                raise ValueError("Retrieve share failed")
            else:
                return share
    
    def get_mean_share(self, request, user_email):
        user = self.user_repository_reader.get_user_by_email(user_email)
        share_name = user.share_cod
        shares = self.share_repository_reader.get_shares_by_share_name(share_name)
        if shares is None:
            raise ValueError("Retrieve mean share failed")
        else:
            n = int(request.n)
            if n < 1:
                raise ValueError("Invalid n")
            limited_shares = shares[:n] if len(shares) > n else shares
            mean = sum([share.value for share in limited_shares]) / len(limited_shares)
            return "Mean value of " + str(share_name) + " of " + str(len(limited_shares)) + " latest shares: " + "{:.3f}".format(mean)
