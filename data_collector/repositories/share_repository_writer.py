import logging
from dto.share import ShareCreationDTO
from models.share_model import Share

logging = logging.getLogger(__name__)

class ShareRepositoryWriter:
    def __init__(self, db):
        self.db = db
        
    def create_share(self, share_dto: ShareCreationDTO):
        share = Share(share_name=share_dto.share_name, value=share_dto.value, timestamp=share_dto.timestamp)
        with self.db.get_db_session() as session:
            try:
                session.add(share)
                session.commit()
                logging.info(f"Share creato: {share}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante la creazione di Share: {e}")
                raise
            return share
    