from sqlalchemy.orm import sessionmaker
from models.ticker_management import TickerManagement
from db.db import get_db_session

def get_ticker_management_by_code(share_cod):
    with get_db_session() as session:
        ticker_management = session.query(TickerManagement).filter_by(share_cod=share_cod).first()
        return ticker_management
    
def get_all_ticker_management():
    with get_db_session() as session:
        ticker_managements = session.query(TickerManagement).all()
        return ticker_managements

def create_ticker_management(share_cod, counter = 0):
    with get_db_session() as session:
        ticker_management = TickerManagement(share_cod=share_cod, counter=counter)
        try:
            session.add(ticker_management)
            session.commit()
            print(f"Ticker management creato: {ticker_management}")
        except Exception as e:
            session.rollback()
            print(f"Errore durante la creazione del ticker management: {e}")
            raise
        return ticker_management

def update_ticker_management(share_cod, counter):
    with get_db_session() as session:
        ticker_management = session.query(TickerManagement).filter_by(share_cod=share_cod).first()
        if ticker_management:
            try:
                ticker_management.counter = counter
                session.commit()
                print(f"Ticker management aggiornato: {ticker_management}")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'aggiornamento del ticker management: {e}")
                raise
        else:
            print("Ticker management non trovato.")

def delete_ticker_management(share_cod):
    with get_db_session() as session:
        ticker_management = session.query(TickerManagement).filter_by(share_cod=share_cod).first()
        if ticker_management:
            try:
                session.delete(ticker_management)
                session.commit()
                print(f"Ticker management eliminato: {ticker_management}")
            except Exception as e:
                session.rollback()
                print(f"Errore durante l'eliminazione del ticker management: {e}")
                raise
        else:
            print("Ticker management non trovato.")
