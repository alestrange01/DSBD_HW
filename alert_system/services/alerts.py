import logging
import time
import json
from confluent_kafka import Consumer, KafkaException, Producer
import json
from repositories import user_repository, share_repository

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

def alerts():
    while True:
        msg = consumer.poll(1.0)  
        if msg is None:
                continue
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                logging.error(f"End of partition reached {msg.topic()} [{msg.partition()}]")
            else:
                logging.error(f"Consumer error: {msg.error()}")
            continue
        data = json.loads(msg.value().decode('utf-8'))
        if data['msg'] != 'Share value updated':     
            logging.error(f"Invalid message received: {data}")
            continue   
        logging.info(f"Consumed: {data}")
        users = user_repository.get_all_users()
        for user in users:
            for user in users:
                latest_share = share_repository.get_latest_share_by_name(user.share_name)
                if latest_share:
                    if (user.high_value != None and latest_share.value > user.high_value) or (user.low_value != None and latest_share.value < user.low_value):
                        if(user.high_value != None and latest_share.value > user.high_value):
                            body = "Il valore del tuo share: {user.share_name} è al limite massimo!"
                        else:
                            body = "Il valore del tuo share: {user.share_name} è al limite minimo!"
                        message = {
                                "to_email":"dr.russodaniele@gmail.com",
                                "subject":"Il valore del tuo share è al limite!",
                                "template_name_html":"email-template.html",
                                "template_name_txt":"email-template.txt",
                                "context":{
                                        "name": user.email,
                                        "message": body,
                                        }
                            }  
                        producer.produce(topic, json.dumps(message), callback=delivery_report)
                        producer.flush() 
                        logging.info(f"Produced: {message}")
                        pass
                else: 
                    continue

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}, retrying...")
        
        message = msg  
        producer.produce(topic, json.dumps(message), callback=delivery_report)
        producer.flush()
        print(f"Produced: {message}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")