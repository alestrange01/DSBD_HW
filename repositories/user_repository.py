from models import User
from db import get_db_session

def get_user_by_email(email):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        return user

def create_user(email, password, share_int):
    with get_db_session() as session:
        user = User(email=email, password=password, share_int=share_int)
        try:
            session.add(user)
            session.commit()
            print(f"Utente creato: {user}")
        except Exception as e:
            session.rollback()
            print(f"Errore durante la creazione dell'utente: {e}")
            raise
        return user

def update_user(email, new_password=None, new_share_int=None):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            try:
                if new_password:
                    user.password = new_password
                if new_share_int is not None:
                    user.share_int = new_share_int
                session.commit()
                print(f"Utente aggiornato: {user}")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'aggiornamento dell'utente: {e}")
                raise
        else:
            print("Utente non trovato.")

def delete_user(email):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            try:
                session.delete(user)
                session.commit()
                print(f"Utente eliminato: {user}")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'eliminazione dell'utente: {e}")
                raise
        else:
            print("Utente non trovato.")

def get_all_users():
    with get_db_session() as session:
        users = session.query(User).all()
        return users
