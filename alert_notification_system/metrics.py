from prometheus_client import Counter, Histogram
import socket

SERVICE_NAME = 'alert_notification_system'
NODE_NAME = socket.gethostname()

messages_consumed = Counter(
    'messages_consumed_total',
    'Number of messages consumed from Kafka',
    ['service', 'node']
)

emails_sent = Counter(
    'emails_sent_total',
    'Number of emails sent successfully',
    ['service', 'node']
)

email_send_errors = Counter(
    'email_send_errors_total',
    'Number of errors sending emails',
    ['service', 'node']
)

email_send_latency = Histogram(
    'email_send_latency_seconds',
    'Email send latency in seconds',
    ['service', 'node']
)