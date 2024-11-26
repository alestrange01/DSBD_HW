import schedule
import time
from services.data_cleaner import clean

if __name__ == '__main__':
    schedule.every().day.do(clean)

    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds() 
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))