from datetime import datetime, timedelta
import logging
import time
from db.db import DB
from repositories.share_repository_reader import ShareRepositoryReader
from repositories.share_repository_writer import ShareRepositoryWriter
from repositories.ticker_management_repository_reader import TickerManagementRepositoryReader
from repositories.ticker_management_repository_writer import TickerManagementRepositoryWriter
from metrics import cleaning_request_duration, shares_deleted, ticker_management_deleted, old_shares_ratio, SERVICE_NAME, NODE_NAME
logging = logging.getLogger(__name__)

class DataCleaner():
    def __init__(self):
        self.db = DB()
        self.share_repository_reader = ShareRepositoryReader(self.db)
        self.share_repository_writer = ShareRepositoryWriter(self.db)
        self.ticker_management_repository_reader = TickerManagementRepositoryReader(self.db)
        self.ticker_management_repository_writer = TickerManagementRepositoryWriter(self.db)
        
    def clean(self):
        with cleaning_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            shares = self.share_repository_reader.get_all_shares()
            total_shares = len(shares)
            old_shares_count = 0
            for share in shares:
                if share.timestamp < datetime.now() - timedelta(days=14):
                    old_shares_count += 1
                    self.share_repository_writer.delete_share(share)
                    shares_deleted.labels(service=SERVICE_NAME, node=NODE_NAME, reason="old").inc()
                    logging.info(f"Share eliminato: {share}, perche' vecchio di 14 giorni.")
            logging.info(f"Totale shares: {total_shares}, shares vecchi eliminati: {old_shares_count}")
            old_shares_ratio.labels(service=SERVICE_NAME, node=NODE_NAME).set(old_shares_count / total_shares if total_shares > 0 else 0)
            ticker_managements = self.ticker_management_repository_reader.get_all_ticker_management()
            for ticker_management in ticker_managements:
                if ticker_management.counter == 0:
                    shares = self.share_repository_reader.get_all_shares_by_share_code(ticker_management.share_cod)
                    for share in shares:
                        self.share_repository_writer.delete_share(share)
                        shares_deleted.labels(service=SERVICE_NAME, node=NODE_NAME, reason="unused").inc()
                        logging.info(f"Share eliminato: {share}, perche' non piu' utilizzato.")
                    self.ticker_management_repository_writer.delete_ticker_management(ticker_management)
                    ticker_management_deleted.labels(service=SERVICE_NAME, node=NODE_NAME).inc()
