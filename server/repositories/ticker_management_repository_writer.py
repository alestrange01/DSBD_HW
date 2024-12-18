import logging
from dto.ticker_management import TickerManagementDTO
from models.ticker_management import TickerManagement

logging = logging.getLogger(__name__)

class TickerManagementRepositoryWriter:
    def __init__(self, session):
        self.session = session
        
    def create_ticker_management(self, ticker_managment_upsert_dto):
        with self.session as session:
            ticker_management = TickerManagement(share_cod=ticker_managment_upsert_dto.share_cod, counter=ticker_managment_upsert_dto.counter)
            try:
                session.add(ticker_management)
                session.commit()
                logging.info(f"Ticker management creato: {ticker_management}")
            except Exception as e:
                session.rollback()
                logging.error(f"Errore durante la creazione del ticker management: {e}")
                raise
            ticker_management_dto = TickerManagementDTO(share_cod=ticker_management.share_cod, counter=ticker_management.counter)
            return ticker_management_dto

    def update_ticker_management(self, ticker_managment_upsert_dto):
        with self.session as session:
            ticker_management = session.query(TickerManagement).filter_by(share_cod=ticker_managment_upsert_dto.share_cod).first()
            if ticker_management:
                try:
                    ticker_management.counter = ticker_managment_upsert_dto.counter
                    session.commit()
                    logging.info(f"Ticker management aggiornato: {ticker_management}")
                except Exception as e:
                    session.rollback()
                    logging.error(f"Errore durante l'aggiornamento del ticker management: {e}")
                    raise
            else:
                logging.info("Ticker management non trovato.")