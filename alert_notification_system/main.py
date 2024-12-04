import logging 
import sys
import threading
import time
from services.alert_notification import send

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('alert_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    alert_thread = threading.Thread(target=send)
    alert_thread.start()
    alert_thread.join()