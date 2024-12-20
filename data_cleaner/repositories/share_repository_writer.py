import logging
from models.share_model import Share

logging = logging.getLogger(__name__)

class ShareRepositoryWriter:
    def __init__(self, db):
        self.db = db
        
    def delete_share(self, share_dto):
        with self.db.get_db_session() as session:
            share = session.query(Share).filter_by(id=share_dto.id).first()
            session.delete(share)
            session.commit()
            logging.info(f"Lo share: {share} è stato eliminato.")

    def delete_shares_by_share_name(self, share_name, batch_size=100): #TODO Unico dubbio, bisogna creare il relativo command o non è necessario qui?
        with self.db.get_db_session() as session:
            try:
                while True:
                    shares = (
                        session.query(Share)
                        .filter_by(share_name=share_name)
                        .order_by(Share.id.asc())
                        .limit(batch_size)
                        .all()
                    )
                    if not shares:
                        break
                    for share in shares:
                        session.delete(share)
                    session.commit()
                    logging.info(f"Eliminato batch di {len(shares)} share per il ticker {share_name}.")
                logging.info(f"Tutti gli share per il ticker {share_name} sono stati eliminati.")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante l'eliminazione degli share per il ticker {share_name}: {e}")
                raise