import logging
from db.db import get_db_session
from models.ticker_management import TickerManagement

logging = logging.getLogger(__name__)

def get_all_ticker_management():
    with get_db_session() as session:
        ticker_managements = session.query(TickerManagement).all()
        return ticker_managements
    
def get_ticker_management_by_code(share_cod):
    with get_db_session() as session:
        ticker_management = session.query(TickerManagement).filter_by(share_cod=share_cod).first()
        return ticker_management

def create_ticker_management(share_cod, counter = 1):
    with get_db_session() as session:
        ticker_management = TickerManagement(share_cod=share_cod, counter=counter)
        try:
            session.add(ticker_management)
            session.commit()
            logging.info(f"Ticker management creato: {ticker_management}")
        except Exception as e:
            session.rollback()
            logging.error(f"Errore durante la creazione del ticker management: {e}")
            raise
        return ticker_management

def update_ticker_management(share_cod, counter):
    with get_db_session() as session:
        ticker_management = session.query(TickerManagement).filter_by(share_cod=share_cod).first()
        if ticker_management:
            try:
                ticker_management.counter = counter
                session.commit()
                logging.info(f"Ticker management aggiornato: {ticker_management}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante l'aggiornamento del ticker management: {e}")
                raise
        else:
            logging.info("Ticker management non trovato.")
