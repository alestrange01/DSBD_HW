from db.db import get_db_session
from models.share_model import Share

def get_all_shares():
    with get_db_session() as session:
        shares = session.query(Share).all()
        return shares
    
def get_all_shares_by_share_code(share_name):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(share_name=share_name).all()
        return shares

def delete_share(share):
    with get_db_session() as session:
        session.delete(share)
        session.commit()
        print(f"Lo share: {share} è stato eliminato.")
        