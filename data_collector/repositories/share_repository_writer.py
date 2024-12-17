import logging
from db.db import get_db_session
from models.share_model import Share
from dto.share import ShareDTO

logging = logging.getLogger(__name__)

def create_share(share_dto: ShareDTO):
    share = Share(share_name=share_dto.share_name, value=share_dto.value, timestamp=share_dto.timestamp)
    with get_db_session() as session:
        try:
            session.add(share)
            session.commit()
            logging.info(f"Share creato: {share}")
        except Exception as e:
            session.rollback()
            logging.error(f"Errore durante la creazione di Share: {e}")
            raise
        return share
    