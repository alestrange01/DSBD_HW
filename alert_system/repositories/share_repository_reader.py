import logging
from dto.share import ShareDTO
from models.share_model import Share

logging = logging.getLogger(__name__)
        
class ShareRepositoryReader:
    def __init__(self, db):
        self.db = db
        
    def get_latest_share_by_name(self, share_name):
        with self.db.get_db_session() as session:
            latest_share = session.query(Share).filter_by(share_name=share_name).order_by(Share.id.desc()).first()
            if latest_share:
                share_dto = ShareDTO(latest_share.value)
                return share_dto
            else:
                logging.error(f"Nessuno share trovato per {share_name}.")
                return None
        