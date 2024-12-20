import logging
import sys
import schedule
import time
import threading
from db.db import DB
from app.server import serve, clean_cache

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    DB.initialize()
    DB.initialize_database()
    serve_thread = threading.Thread(target=serve, daemon=True)
    serve_thread.start()

    schedule.every(5).minutes.do(clean_cache)
    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds()  
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))   
    