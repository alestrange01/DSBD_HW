import logging
import time
from datetime import datetime, timedelta
from data_cleaner.repositories import ticker_management_repository_reader, ticker_management_repository_writer
from data_cleaner.repositories import share_repository_reader, share_repository_writer

logging = logging.getLogger(__name__)

def clean():
    shares = share_repository_reader.get_all_shares()
    for share in shares:
        if share.timestamp < datetime.now() - timedelta(days=14):
            share_repository_writer.delete_share(share)
            logging.info(f"Share eliminato: {share}, perche' vecchio di 14 giorni.")
    ticker_management = ticker_management_repository_reader.get_all_ticker_management()
    for ticker in ticker_management:
        if ticker.counter == 0:
            shares = share_repository_reader.get_all_shares_by_share_code(ticker.share_cod)
            for share in shares:
                share_repository_writer.delete_share(share)
                logging.info(f"Share eliminato: {share}, perche' non piu' utilizzato.")
            ticker_management_repository_writer.delete_ticker_management(ticker.share_cod)
