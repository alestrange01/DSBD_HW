import schedule
import time
from services.data_cleaner import clean

if __name__ == '__main__':
    schedule.every(5).minutes.do(clean())

    while True:
        schedule.run_pending()
        time.sleep(1) 