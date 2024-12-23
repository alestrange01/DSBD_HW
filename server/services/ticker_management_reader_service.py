import logging
from db.db import DB
from repositories.ticker_management_repository_reader import TickerManagementRepositoryReader

logging = logging.getLogger(__name__)

class TickerManagementReaderService: 
    def __init__(self):
        self.db = DB()
        self.ticker_management_repository_reader = TickerManagementRepositoryReader(self.db)
        
    def get_all_ticker_managements(self):
        ticker_managements = self.ticker_management_repository_reader.get_all_ticker_management()
        if ticker_managements is None:
            raise ValueError("Ticker management not found")
        else:
            return ticker_managements