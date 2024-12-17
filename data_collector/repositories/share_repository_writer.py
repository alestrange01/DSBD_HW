import logging
from models.share_model import Share
from dto.share import ShareCreationDTO

logging = logging.getLogger(__name__)

class ShareRepositoryWriter:
    def __init__(self, session):
        self.session = session
        
    def create_share(self, share_dto: ShareCreationDTO):
        share = Share(share_name=share_dto.share_name, value=share_dto.value, timestamp=share_dto.timestamp)
        with self.session as session:
            try:
                session.add(share)
                session.commit()
                logging.info(f"Share creato: {share}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante la creazione di Share: {e}")
                raise
            return share
    