import logging 
import sys
from services.kafka_manager import KafkaManager
import schedule
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('kafka_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
bootstrap_servers = ['kafka-broker-1:9092', 'kafka-broker-2:9092', 'kafka-broker-3:9092']
topic_list = ['to-alert-system', 'to-notifier']
num_partitions = 1  
replication_factor = 3  

if __name__ == "__main__":
    kafka_manager = KafkaManager(bootstrap_servers=bootstrap_servers)
    try:
        logger.info("Creazione dei topic (se non esistenti...)\n")
        kafka_manager.create_topic_if_not_exists(topic_list, num_partitions=num_partitions, replication_factor=replication_factor)
        logger.info("Stampa dei dettagli dei topic...")
        kafka_manager.list_topics_and_details()     
        schedule.every(3).minutes.do(kafka_manager.get_metadata)   
    except Exception as e:
        logger.error(f"Errore: {e}")
        exit(1)

    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds()  
        if next_run is None or next_run < 0:
            next_run = 1  
        time.sleep(min(next_run, 60))  
