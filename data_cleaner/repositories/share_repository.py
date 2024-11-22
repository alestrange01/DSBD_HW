from sqlalchemy.orm import sessionmaker
from models.share_model import Share
from db.db import get_db_session

def get_all_shares():
    with get_db_session() as session:
        shares = session.query(Share).all()
        return shares
    
def get_all_shares_by_share_code(share_name):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(share_name=share_name).all()
        return shares

def delete_shares_by_share_name(share_name):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(share_name=share_name).all()
        if shares:
            try:
                for share in shares:
                    session.delete(share)
                session.commit()
                print(f"Tutti gli share per il ticker {share_name} sono stati eliminati.")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'eliminazione degli share per il ticker {share_name}: {e}")
                raise
        else:
            print(f"Nessun share trovato per il ticker con ID {share_name}.")

def delete_share(share):
    with get_db_session() as session:
        session.delete(share)
        session.commit()
        print(f"Lo share: {share} è stato eliminato.")


def close_session():
    with get_db_session() as session:
        session.close()