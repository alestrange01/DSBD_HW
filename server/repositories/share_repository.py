from sqlalchemy.orm import sessionmaker
from models.share_model import Share
from db.db import get_db_session


def get_shares_by_user_id(user_id):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(user_id=user_id).all()
        if shares:
            return shares
        else:
            print(f"Nessuno share trovato per l'utente con ID {user_id}.")
            return None

def create_share(user_id, share_name, value, timestamp):
    share = Share(share_name=share_name, value=value, user_id=user_id, timestamp=timestamp)
    with get_db_session() as session:
        try:
            session.add(share)
            session.commit()
            print(f"Share creato: {share}")
        except Exception as e:
            session.rollback()
            print(f"Errore durante la creazione di Share: {e}")
            raise
        return share

def get_share_by_id(share_id):
    with get_db_session() as session:
        share = session.query(Share).filter_by(id=share_id).first()
        if share:
            return share
        else:
            print(f"Share con ID {share_id} non trovato.")
            return None

def delete_share(share_id):
    with get_db_session() as session:
        share = get_share_by_id(share_id)
        if share:
            try:
                session.delete(share)
                session.commit()
                print(f"Share eliminato: {share}")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'eliminazione di Share: {e}")
                raise
        else:
            print("Share non trovato.")

def delete_shares_by_user(user_id):
    with get_db_session() as session:
        shares = session.query(Share).filter_by(user_id=user_id).all()
        if shares:
            try:
                for share in shares:
                    session.delete(share)
                session.commit()
                print(f"Tutti gli share per l'utente {user_id} sono stati eliminati.")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'eliminazione degli share per l'utente {user_id}: {e}")
                raise
        else:
            print(f"Nessun share trovato per l'utente con ID {user_id}.")

def close_session():
    with get_db_session() as session:
        session.close()