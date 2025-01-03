import logging 
import sys
import schedule
import time
from services.data_cleaner import DataCleaner
from db.db import DB
from prometheus_client import start_http_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('data_cleaner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


if __name__ == '__main__':
    DB.initialize()
    data_cleaner = DataCleaner()
    schedule.every().day.do(data_cleaner.clean) 
    start_http_server(50056)

    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds() 
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))