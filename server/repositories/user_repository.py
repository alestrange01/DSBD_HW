import logging
from db.db import get_db_session
from models.user_model import User

logging = logging.getLogger(__name__)

def get_all_users():
    with get_db_session() as session:
        users = session.query(User).all()
        return users
    
def get_user_by_email(email):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        return user

def create_user(email, password, share_cod, role="user", high_value=None, low_value=None):
    with get_db_session() as session:
        user = User(email=email, password=password, role=role, share_cod=share_cod, high_value=high_value, low_value=low_value)
        try:
            session.add(user)
            session.commit()
            logging.info(f"Utente creato: {user}")
        except Exception as e:
            session.rollback()
            logging.error(f"Errore durante la creazione dell'utente: {e}")
            raise
        return user

def update_user(email, new_password=None, new_share_cod=None, new_high_value=None, new_low_value=None):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            try:
                if new_password:
                    user.password = new_password
                if new_share_cod is not None:
                    user.share_cod = new_share_cod
                if new_high_value is not None:
                    if new_low_value is not None:
                        if new_high_value <= new_low_value:
                            raise ValueError("new_high_value must be greater than new_low_value")
                    elif user.low_value is not None and new_high_value <= user.low_value:
                        raise ValueError("new_high_value must be greater than the current low_value")
                    user.high_value = new_high_value
                if new_low_value is not None:
                    if user.high_value is not None and new_low_value >= user.high_value:
                        raise ValueError("new_low_value must be less than the current high_value")
                    user.low_value = new_low_value
                session.commit()
                logging.info(f"Utente aggiornato: {user}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante l'aggiornamento dell'utente: {e}")
                raise
        else:
            logging.info("Utente non trovato.")

def delete_user(email):
    with get_db_session() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            try:
                session.delete(user)
                session.commit()
                logging.info(f"Utente eliminato: {user}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante l'eliminazione dell'utente: {e}")
                raise
        else:
            logging.info("Utente non trovato.")
