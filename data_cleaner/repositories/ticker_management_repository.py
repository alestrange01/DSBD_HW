import logging
from db.db import get_db_session
from models.ticker_management import TickerManagement

logging = logging.getLogger(__name__)

def get_all_ticker_management():
    with get_db_session() as session:
        ticker_managements = session.query(TickerManagement).all()
        return ticker_managements
    
def delete_ticker_management(ticker_management):
    with get_db_session() as session:
        ticker_management = session.query(TickerManagement).filter_by(share_cod=ticker_management).first()
        if ticker_management:
            try:
                session.delete(ticker_management)
                session.commit()
                logging.info(f"Lo share: {ticker_management} è stato eliminato.")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante l'eliminazione dello share: {e}")
                raise
        else:
            logging.info("Ticker non trovato.")