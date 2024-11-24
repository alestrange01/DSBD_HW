from db.db import get_db_session
from models.user_model import User

def get_all_users():
    with get_db_session() as session:
        users = session.query(User).all()
        return users
    
def get_user_by_email(email):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        return user

def create_user(email, password, share_cod, role="user"):
    with get_db_session() as session:
        user = User(email=email, password=password, role=role, share_cod=share_cod)
        try:
            session.add(user)
            session.commit()
            print(f"Utente creato: {user}")
        except Exception as e:
            session.rollback()
            print(f"Errore durante la creazione dell'utente: {e}")
            raise
        return user

def update_user(email, new_password=None, new_share_cod=None):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            try:
                if new_password:
                    user.password = new_password
                if new_share_cod is not None:
                    user.share_cod = new_share_cod
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
