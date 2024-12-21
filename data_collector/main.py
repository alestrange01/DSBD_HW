import logging
import sys
import schedule
import time
from db.db import DB
from services.data_collector import DataCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('data_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    DB.initialize()
    DB.initialize_database()   
    data_collector = DataCollector()
    #data_collector.test_circuit_breaker_behavior() #TOTEST rimuovere il commento per testare il circuit breaker
    schedule.every(1).seconds.do(data_collector.collect) #TODO modificare

    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds()  
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))  