import logging 
import sys
import threading
from services.alerts import Alerts
from db.db import DB
from prometheus_client import start_http_server

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
    start_http_server(50057)
    alert = Alerts()
    alert_thread = threading.Thread(target=alert.alerts)
    alert_thread.start()
    alert_thread.join()