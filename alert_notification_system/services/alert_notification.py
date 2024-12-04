import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import json
import logging
from confluent_kafka import Consumer, KafkaException

logging = logging.getLogger(__name__)

consumer_config = {
    'bootstrap.servers': 'localhost:29092',  
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

def send(data):
    to_email = data["email"]
    subject = data["subject"]
    template_name_html = data["template_name_html"]
    template_name_txt = data["template_name_txt"]
    context = data["context"]
    html_content = render_template("./html/" + template_name_html, context)
    text_content = render_template("./text/" + template_name_txt, context)

    msg = MIMEMultipart("alternative")
    msg["From"] = "fraromeo69@gmail.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("fraromeo69@gmail.com", "nxis zslg ywts rpyj")
        server.sendmail(msg["From"], to_email, msg.as_string())
    
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

def send_email():
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
        logging.info(f"Consumed: {data}")
        send(data)
