import logging
import time
from datetime import datetime, timedelta
from db.db import DB
from repositories.share_repository_reader import ShareRepositoryReader
from repositories.share_repository_writer import ShareRepositoryWriter
from repositories.ticker_management_repository_reader import TickerManagementRepositoryReader
from repositories.ticker_management_repository_writer import TickerManagementRepositoryWriter

logging = logging.getLogger(__name__)

class DataCleaner():
    def __init__(self):
        self.DB = DB()
        self.db_session = self.DB.get_db_session()
        self.share_repository_reader = ShareRepositoryReader(self.db_session)
        self.share_repository_writer = ShareRepositoryWriter(self.db_session)
        self.ticker_management_repository_reader = TickerManagementRepositoryReader(self.db_session)
        self.ticker_management_repository_writer = TickerManagementRepositoryWriter(self.db_session)
        
    def clean(self):
        shares = self.share_repository_reader.get_all_shares()
        for share in shares:
            if share.timestamp < datetime.now() - timedelta(days=14):
                self.share_repository_writer.delete_share(share)
                logging.info(f"Share eliminato: {share}, perche' vecchio di 14 giorni.")
        ticker_managements = self.ticker_management_repository_reader.get_all_ticker_management()
        for ticker_management in ticker_managements:
            if ticker_management.counter == 0:
                shares = self.share_repository_reader.get_all_shares_by_share_code(ticker_management.share_cod)
                for share in shares:
                    self.share_repository_writer.delete_share(share)
                    logging.info(f"Share eliminato: {share}, perche' non piu' utilizzato.")
                self.ticker_management_repository_writer.delete_ticker_management(ticker_management)
