import logging 
import sys
import threading
from services.alert_notification import consume_and_send_notifications

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('alert_notification_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    alert_thread = threading.Thread(target=consume_and_send_notifications)
    alert_thread.start()
    alert_thread.join()