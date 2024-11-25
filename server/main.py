import schedule
import time
import threading
from db.db import initialize_database
from services.server import serve, start_cleaner_thread

if __name__ == '__main__':
    initialize_database()
    serve_thread = threading.Thread(target=serve, daemon=True)
    serve_thread.start()

    schedule.every(5).minutes.do(start_cleaner_thread())
    while True:
        schedule.run_pending()
        time.sleep(1)     
    