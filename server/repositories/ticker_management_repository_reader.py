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
