from confluent_kafka import Consumer, KafkaError, Producer
import logging
import time
import json
import json
from db.db import DB
from repositories.user_repository_reader import UserRepositoryReader
from repositories.share_repository_reader import ShareRepositoryReader

logging = logging.getLogger(__name__)

class Alerts:
    def __init__(self):
        producer_config = {
            'bootstrap.servers': 'kafka-broker:9092',  
            'acks': 'all',  
            'batch.size': 500,  
            'linger.ms': 500,
            'max.in.flight.requests.per.connection': 1, 
            'retries': 3 
        }
        self.producer = Producer(producer_config)
        self.topic = "to-notifier"

        consumer_config = {
            'bootstrap.servers': 'kafka-broker:9092',  
            'group.id': 'group1', 
            'auto.offset.reset': 'earliest',  
            'enable.auto.commit': False
        }

        self.consumer = Consumer(consumer_config) 
        topic2 = 'to-alert-system'  
        self.consumer.subscribe([topic2])
        self.db = DB()
        self.user_repository_reader = UserRepositoryReader(self.db)
        self.share_repository_reader = ShareRepositoryReader(self.db)



    def alerts(self):
            try:
                while True:
                    self.__process_message()
            except KeyboardInterrupt:
                logging.info("Consumer interrupted by user. Shutting down gracefully.")
            finally:
                self.consumer.close()
                logging.info("Consumer closed.")

    def __process_message(self):
        try:
            msg = self.consumer.poll(1.0)
            if msg is None:
                return
            if msg.error():
                self.__handle_consumer_error(msg)
                return
            self.__handle_message(msg)
        except Exception as e:
            logging.error(f"Unexpected error in Kafka consumer loop: {e}")

    def __handle_consumer_error(self, msg):
        if msg.error().code() == KafkaError._PARTITION_EOF:
            logging.error(f"End of partition reached {msg.topic()} [{msg.partition()}]")
        else:
            logging.error(f"Consumer error: {msg.error()}")

    def __handle_message(self, msg):
        try:
            data = json.loads(msg.value().decode('utf-8'))
            logging.info(f"Consumed: {data}")
            if self.__process(data):
                self.consumer.commit(asynchronous=False)
                logging.info(f"Offset committed: {msg.offset()}")
            else:
                logging.error(f"Error processing message: {data}")
        except Exception as e:
            logging.error(f"Unexpected error processing message: {e}")

    def __process(self, data):
        try:
            if data['msg'] != 'Share value updated':
                logging.error(f"Invalid message received: {data}")
                return False
            logging.info(f"Consumed __process: {data}")
            users = self.user_repository_reader.get_all_users()
            for user in users:
                latest_share = self.share_repository_reader.get_latest_share_by_name(user.share_cod)
                if latest_share:
                    high_value_exceeded = user.high_value is not None and latest_share.value > user.high_value
                    low_value_exceeded = user.low_value is not None and latest_share.value < user.low_value
                    if high_value_exceeded or low_value_exceeded:
                        limite = "massimo" if high_value_exceeded else "minimo"
                        body = f"Il valore del tuo share: {user.share_cod} è al limite {limite}: {latest_share.value}!"
                        message = {
                            "to": user.email,
                            "subject": "Valore al limite:" + str(user.share_cod),
                            "template_name_html": "email-template.html",
                            "template_name_txt": "email-template.txt",
                            "context": {
                                "name": user.email,
                                "message": body,
                            },
                        }
                        self.producer.produce(self.topic, json.dumps(message), callback=self.__delivery_report)
                        self.producer.flush()
                        logging.info(f"Produced: {message}")
            return True
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            return False

    def __delivery_report(self, err, msg):
        if err:
            print(f"Delivery failed: {err}, retrying...")
            message = msg  
            self.producer.produce(self.topic, json.dumps(message), callback=self.__delivery_report)
            self.producer.flush()
            print(f"Produced: {message}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")