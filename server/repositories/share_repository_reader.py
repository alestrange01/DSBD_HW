import logging
from models.share_model import Share
from dto.share import ShareDTO

logging = logging.getLogger(__name__)

class ShareRepositoryReader:
    def __init__(self, session):
        self.session = session
        
    def get_all_shares(self):
        with self.session as session:
            shares = session.query(Share).all()
            shares_dto = []
            for share in shares:
                share_dto = ShareDTO(share_name=share.share_name, value=share.value, timestamp=share.timestamp)
                shares_dto.append(share_dto)
            return shares_dto

    def get_shares_by_share_name(self, share_name):
        with self.session as session:
            shares = session.query(Share).filter_by(share_name=share_name).order_by(Share.id.desc()).all()
            if shares:
                shares_dto = []
                for share in shares:
                    share_dto = ShareDTO(share_name=share.share_name, value=share.value, timestamp=share.timestamp)
                    shares_dto.append(share_dto)
                return shares_dto
            else:
                logging.error(f"Nessuno share trovato per {share_name}.")
                return None
            
    def get_latest_share_by_name(self, share_name):
        with self.session as session:
            latest_share = session.query(Share).filter_by(share_name=share_name).order_by(Share.id.desc()).first()
            if latest_share:
                latest_share_dto = ShareDTO(share_name=latest_share.share_name, value=latest_share.value, timestamp=latest_share.timestamp)
                return latest_share_dto
            else:
                logging.error(f"Nessuno share trovato per {share_name}.")
                return None
        