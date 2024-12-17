import logging
import sys
import schedule
import time
from db.db import initialize_database
from services.data_collector import collect, test_circuit_breaker_behavior

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('data_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    initialize_database()    
    #test_circuit_breaker_behavior() #TOTEST rimuovere il commento per testare il circuit breaker
    schedule.every(10).minutes.do(collect)

    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds()  
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))  