import logging
from db.db import get_db_session
from models.share_model import Share

logging = logging.getLogger(__name__)

def create_share(share_name, value, timestamp):
    share = Share(share_name=share_name, value=value, timestamp=timestamp)
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
    