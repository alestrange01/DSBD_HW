import schedule
import time
from db.db import initialize_database
from services.data_collector import collect, test_circuit_breaker_behavior

if __name__ == '__main__':
    initialize_database()    
    #test_circuit_breaker_behavior() rimuovere il commento per testare il circuit breaker
    schedule.every(10).minutes.do(collect)

    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds()  
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))  