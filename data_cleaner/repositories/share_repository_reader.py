import logging
from dto.share import ShareDTO
from models.share_model import Share

logging = logging.getLogger(__name__)

class ShareRepositoryReader:
    def __init__(self, session):
        self.db_session = session
        
    def get_all_shares(self):
        with self.db_session as session:
            shares = session.query(Share).all()
            shares_dto = []
            for share in shares:
                share_dto = ShareDTO(share.id, share.timestamp)
                shares_dto.append(share_dto)
            return shares_dto
        
    def get_all_shares_by_share_code(self,share_name):
        with self.db_session as session:
            shares = session.query(Share).filter_by(share_name=share_name).all()
            shares_dto = []
            for share in shares:
                share_dto = ShareDTO(share.id, share.timestamp)
                shares_dto.append(share_dto)
            return shares_dto
