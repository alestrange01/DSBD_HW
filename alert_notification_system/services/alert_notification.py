from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from confluent_kafka import Consumer, KafkaError
import smtplib
import json
import logging
import os

logging = logging.getLogger(__name__) 

class AlertNotification:
    def __init__(self):

        self.email_sender_user = os.getenv('EMAIL_SENDER_USER', "")
        self.email_sender_password = os.getenv('EMAIL_SENDER_PASSWORD', "")

        consumer_config = {
            'bootstrap.servers': 'kafka-broker:9092',  
            'group.id': 'group2', 
            'auto.offset.reset': 'earliest',  
            'enable.auto.commit': True 
        }

        self.consumer = Consumer(consumer_config) 
        topic = 'to-notifier' 
        self.consumer.subscribe([topic])

        self.template_loader = FileSystemLoader(searchpath="./templates") 
        self.env = Environment(loader=self.template_loader)

    def __render_template(self,template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def __deliver_email(self,data):
        try:
            recipient = data["to"]
            ticker = data["subject"]
            template_name_html = data["template_name_html"]
            template_name_txt = data["template_name_txt"]
            context = data["context"]
            html_content = self.__render_template("./html/" + template_name_html, context)
            text_content = self.__render_template("./text/" + template_name_txt, context)

            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_sender_user
            msg["To"] = recipient
            msg["Subject"] = ticker
            
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email_sender_user, self.email_sender_password)
                server.sendmail(msg["From"], msg["To"], msg.as_string())
            
            logging.info(f"Email sent to {recipient}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email to {recipient}: {e}")
            return False

    def __handle_message(self, msg):
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logging.error(f"End of partition reached {msg.topic()} [{msg.partition()}]")
            else:
                logging.error(f"Consumer error: {msg.error()}")
            return False
        return True

    def __process_message(self, msg):
        data = json.loads(msg.value().decode('utf-8'))
        logging.info(f"Consumed: {data}")
        if self.__deliver_email(data):
            #self.consumer.commit(asynchronous=False) #TODO Il commit non va fatto a priori?
            logging.info(f"Offset committed for message: {msg.offset()}")
        else:
            logging.error(f"Failed to process email notification: {data}")

    def consume_and_send_notifications(self):
        try:
            while True:
                try:
                    msg = self.consumer.poll(1.0)
                    if msg is None:
                        continue
                    if not self.__handle_message(msg):
                        continue
                    self.__process_message(msg)
                except Exception as e:
                    logging.error(f"Unexpected error in Kafka consumer loop: {e}")
        except KeyboardInterrupt:
            logging.info("Consumer interrupted by user. Shutting down gracefully.")
        finally:
            self.consumer.close()
            logging.info("Consumer closed.")