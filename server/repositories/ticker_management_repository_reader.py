import logging
from dto.ticker_management import TickerManagementDTO
from models.ticker_management import TickerManagement

logging = logging.getLogger(__name__)

class TickerManagementRepositoryReader:
    def __init__(self, db):
        self.db = db
        
    def get_all_ticker_management(self):
        with self.db.get_db_session() as session:
            ticker_managements = session.query(TickerManagement).all()
            return ticker_managements
        
    def get_ticker_management_by_code(self, share_cod):
        with self.db.get_db_session() as session:
            ticker_management = session.query(TickerManagement).filter_by(share_cod=share_cod).first()
            ticker_management_dto = TickerManagementDTO(share_cod=ticker_management.share_cod, counter=ticker_management.counter)
            return ticker_management_dto
