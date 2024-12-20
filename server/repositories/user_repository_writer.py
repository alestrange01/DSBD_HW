import logging
from dto.user import UserCreationDTO
from models.user_model import User

logging = logging.getLogger(__name__)

class UserRepositoryWriter:
    def __init__(self, db):
        self.db = db
        
    def create_user(self, user_creation_dto: UserCreationDTO):
        with self.db.get_db_session() as session:
            user = User(email=user_creation_dto.email, password=user_creation_dto.password, role=user_creation_dto.role, share_cod=user_creation_dto.share_cod, high_value=user_creation_dto.high_value, low_value=user_creation_dto.low_value)
            try:
                session.add(user)
                session.commit()
                logging.info(f"Utente creato: {user}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante la creazione dell'utente: {e}")
                raise
            return user

    def update_user(self, user_update_dto):
        with self.db.get_db_session() as session:
            user = session.query(User).filter_by(email=user_update_dto.email).first()
            if user:
                try:
                    if user_update_dto.new_password:
                        user.password = user_update_dto.new_password
                    if user_update_dto.new_share_cod is not None:
                        user.share_cod = user_update_dto.new_share_cod
                    if user_update_dto.new_high_value is not None:
                        if user_update_dto.new_low_value is not None:
                            if user_update_dto.new_high_value <= user_update_dto.new_low_value:
                                raise ValueError("new_high_value must be greater than new_low_value")
                        elif user.low_value is not None and user_update_dto.new_high_value <= user.low_value:
                            raise ValueError("new_high_value must be greater than the current low_value")
                        user.high_value = user_update_dto.new_high_value
                    if user_update_dto.new_low_value is not None:
                        if user.high_value is not None and user_update_dto.new_low_value >= user.high_value:
                            raise ValueError("new_low_value must be less than the current high_value")
                        user.low_value = user_update_dto.new_low_value
                    session.commit()
                    logging.info(f"Utente aggiornato: {user}")
                except Exception as e:
                    session.rollback()
                    logging.error(f"Errore durante l'aggiornamento dell'utente: {e}")
                    raise
            else:
                logging.info("Utente non trovato.")

    def delete_user(self, email):
        with self.db.get_db_session() as session:
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