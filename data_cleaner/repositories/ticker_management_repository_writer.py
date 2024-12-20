import logging
from models.ticker_management import TickerManagement

logging = logging.getLogger(__name__)

class TickerManagementRepositoryWriter:
    def __init__(self, db):
        self.db = db
        
    def delete_ticker_management(self, ticker_management):
        with self.db.get_db_session() as session:
            ticker_management = session.query(TickerManagement).filter_by(share_cod=ticker_management.share_cod).first()
            if ticker_management:
                try:
                    session.delete(ticker_management)
                    session.commit()
                    logging.info(f"Il ticker: {ticker_management} è stato eliminato.")
                except Exception as e:
                    session.rollback()
                    logging.error(f"Errore durante l'eliminazione del ticker: {e}")
                    raise
            else:
                logging.info("Ticker non trovato.")