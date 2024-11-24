import time
from datetime import datetime, timedelta
from repositories import ticker_management_repository
from repositories import share_repository

def clean():
    while True:
        shares = share_repository.get_all_shares()
        for share in shares:
            if share.timestamp < datetime.now() - timedelta(days=14):
                share_repository.delete_share(share)
                print(f"Share eliminato: {share}, perche' vecchio di 14 giorni.")
        ticker_management = ticker_management_repository.get_all_ticker_management()
        for ticker in ticker_management:
            if ticker.counter == 0:
                shares = share_repository.get_all_shares_by_share_code(ticker.share_cod)
                for share in shares:
                    share_repository.delete_share(share)
                    print(f"Share eliminato: {share}, perche' non piu' utilizzato.")
        time.sleep(300)

