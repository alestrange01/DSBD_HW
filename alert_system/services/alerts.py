import logging
import time
import json
from confluent_kafka import Consumer, KafkaException, Producer
import json
from alert_system.repositories import share_repository_reader
from alert_system.repositories import user_repository_reader

producer_config = {
    'bootstrap.servers': 'localhost:29092',  
    'acks': 'all',  
    'batch.size': 500,  
    'max.in.flight.requests.per.connection': 1, 
    'retries': 3 
}
producer = Producer(producer_config)
topic = "to-notifier"

consumer_config = {
    'bootstrap.servers': 'localhost:29092',  
    'group.id': 'group2', 
    'auto.offset.reset': 'earliest',  
    'enable.auto.commit': False 
}

consumer = Consumer(consumer_config) 
topic2 = 'to-alert-system'  
consumer.subscribe([topic2])

logging = logging.getLogger(__name__)

def process(data):
    try:
        if data['msg'] != 'Share value updated':
            logging.error(f"Invalid message received: {data}")
            return False
        logging.info(f"Consumed: {data}")
        users = user_repository_reader.get_all_users()
        for user in users:
            latest_share = share_repository_reader.get_latest_share_by_name(user.share_name)
            if latest_share:
                high_value_exceeded = user.high_value is not None and latest_share.value > user.high_value
                low_value_exceeded = user.low_value is not None and latest_share.value < user.low_value
                if high_value_exceeded or low_value_exceeded:
                    limite = "massimo" if high_value_exceeded else "minimo"
                    body = f"Il valore del tuo share: {user.share_name} è al limite {limite}: {latest_share.value}!"
                    message = {
                        "to": user.email,
                        "subject": str(user.share_name),
                        "template_name_html": "email-template.html",
                        "template_name_txt": "email-template.txt",
                        "context": {
                            "name": user.email,
                            "message": body,
                        },
                    }
                    producer.produce(topic, json.dumps(message), callback=delivery_report)
                    producer.flush()
                    logging.info(f"Produced: {message}")
        return True
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return False



def alerts():
    try:
        while True:
            try:
                msg = consumer.poll(1.0)  
                if msg is None:
                        continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        logging.error(f"End of partition reached {msg.topic()} [{msg.partition()}]")
                    else:
                        logging.error(f"Consumer error: {msg.error()}")
                    continue
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    logging.info(f"Consumed: {data}")
                    if process(data):
                        consumer.commit(asynchronous=False)
                        logging.info(f"Offset committed: {msg.offset()}")
                    else:
                        logging.error(f"Error processing message: {data}")
                except Exception as e:
                    logging.error(f"Unexpected error processing message: {e}")
            except Exception as e:
                logging.error(f"Unexpected error in Kafka consumer loop: {e}")
    except KeyboardInterrupt:
        logging.info("Consumer interrupted by user. Shutting down gracefully.")
    finally:
        consumer.close()
        logging.info("Consumer closed.")

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}, retrying...")
        
        message = msg  
        producer.produce(topic, json.dumps(message), callback=delivery_report)
        producer.flush()
        print(f"Produced: {message}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")