import logging 
import sys
import threading
from services.alerts import Alerts
from db.db import DB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('alert_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    DB.initialize()
    alert = Alerts()
    alert_thread = threading.Thread(target=alert.alerts)
    alert_thread.start()
    alert_thread.join()