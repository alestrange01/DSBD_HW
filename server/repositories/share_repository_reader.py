import logging
from db.db import get_db_session
from models.share_model import Share

logging = logging.getLogger(__name__)

def get_all_shares():
    with get_db_session() as session:
        shares = session.query(Share).all()
        return shares

def get_shares_by_share_name(share_name):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(share_name=share_name).order_by(Share.id.desc()).all()
        if shares:
            return shares
        else:
            logging.error(f"Nessuno share trovato per {share_name}.")
            return None
        
def get_latest_share_by_name(share_name):
    with get_db_session() as session:
        latest_share = session.query(Share).filter_by(share_name=share_name).order_by(Share.id.desc()).first()
        if latest_share:
            return latest_share
        else:
            logging.error(f"Nessuno share trovato per {share_name}.")
            return None
        