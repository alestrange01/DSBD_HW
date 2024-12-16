import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import json
import logging
from confluent_kafka import Consumer, KafkaException

logging = logging.getLogger(__name__)

consumer_config = {
    'bootstrap.servers': 'kafka:9092',  
    'group.id': 'group2', 
    'auto.offset.reset': 'earliest',  
    'enable.auto.commit': False 
}

consumer = Consumer(consumer_config) 
topic = 'to-notifier'  
consumer.subscribe([topic])

template_loader = FileSystemLoader(searchpath="./templates") 
env = Environment(loader=template_loader)

def render_template(template_name, context):
    template = env.get_template(template_name)
    return template.render(context)

def deliver_email(data):
    try:
        recipient = data["to"]
        ticker = data["subject"]
        template_name_html = data["template_name_html"]
        template_name_txt = data["template_name_txt"]
        context = data["context"]
        html_content = render_template("./html/" + template_name_html, context)
        text_content = render_template("./text/" + template_name_txt, context)

        msg = MIMEMultipart("alternative")
        msg["From"] = "fraromeo69@gmail.com"
        msg["To"] = recipient
        msg["Subject"] = ticker
        
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("fraromeo69@gmail.com", "nxis zslg ywts rpyj") #TODO: rendere sicura la password
            server.sendmail(msg["From"], msg["To"], msg.as_string())
        
        logging.info(f"Email sent to {recipient}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {e}")
        return False

    
# body = "Il valore del tuo share: AAPL è al limite minimo!"
# message = {
#         "to_email":"dr.russodaniele@gmail.com",
#         "subject":"Il valore del tuo share è al limite!",
#         "template_name_html":"email-template.html",
#         "template_name_txt":"email-template.txt",
#         "context":{
#                 "name": "Daniele",
#                 "message": body,
#                 }
#     }  
# send_email(
#     data = message
# )

def consume_and_send_notifications():
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
                data = json.loads(msg.value().decode('utf-8'))
                logging.info(f"Consumed: {data}")
                try:
                    if deliver_email(data):
                        consumer.commit(asynchronous=False)
                        logging.info(f"Offset committed for message: {msg.offset()}")
                    else:
                        logging.error(f"Failed to process email notification: {data}")
                except Exception as e:
                    logging.error(f"Unexpected error processing email notification: {e}")
            except Exception as e:
                logging.error(f"Unexpected error in Kafka consumer loop: {e}")
    except KeyboardInterrupt:
        logging.info("Consumer interrupted by user. Shutting down gracefully.")
    finally:
        consumer.close()
        logging.info("Consumer closed.")
