import logging
from db.db import get_db_session
from models.share_model import Share

logging = logging.getLogger(__name__)

def get_all_shares():
    with get_db_session() as session:
        shares = session.query(Share).all()
        return shares
    
def get_all_shares_by_share_code(share_name):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(share_name=share_name).all()
        return shares
