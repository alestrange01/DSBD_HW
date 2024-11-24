from db.db import get_db_session
from models.ticker_management import TickerManagement

def get_all_ticker_management():
    with get_db_session() as session:
        ticker_managements = session.query(TickerManagement).all()
        return ticker_managements
    