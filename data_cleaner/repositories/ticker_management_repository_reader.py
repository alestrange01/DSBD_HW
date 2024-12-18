import logging
from dto.ticker_management import TickeManagementDTO
from models.ticker_management import TickerManagement

logging = logging.getLogger(__name__)

class TickerManagementRepositoryReader:
    def __init__(self, session):
        self.db_session = session
        
    def get_all_ticker_management(self):
        with self.db_session as session:
            ticker_managements = session.query(TickerManagement).all()
            ticker_managements_dto = []
            for ticker_management in ticker_managements:
                ticker_management_dto = TickeManagementDTO(ticker_management.share_cod)
                ticker_managements_dto.append(ticker_management_dto)
            return ticker_managements_dto
    