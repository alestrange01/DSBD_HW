from sqlalchemy.orm import sessionmaker
from models import Share
from db import get_db_session

session = get_db_session()

def get_shares_by_user_id(user_id):
    shares = session.query(Share).filter_by(user_id=user_id).all()
    return shares

def create_share(user_id, share_name, value):
    share = Share(share_name=share_name, value=value, user_id=user_id)
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
    share = session.query(Share).filter_by(id=share_id).first()
    return share

def delete_share(share_id):
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
    session.close()