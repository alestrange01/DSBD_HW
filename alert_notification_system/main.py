import logging 
import sys
import threading
from services.alert_notification import AlertNotification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('alert_notification_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    alert_notification = AlertNotification()
    alert_thread = threading.Thread(target=alert_notification.consume_and_send_notifications) #TODO Rendere private tutte tranne questa
    alert_thread.start()
    alert_thread.join()