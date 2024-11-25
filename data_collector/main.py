import schedule
import time
from db.db import initialize_database
from services.data_collector import collect, test_circuit_breaker_behavior

if __name__ == '__main__':
    initialize_database()    
    schedule.every(5).minutes.do(collect())
    schedule.every(15).minutes.do(test_circuit_breaker_behavior())
    while True:
        schedule.run_pending()
        time.sleep(1) 