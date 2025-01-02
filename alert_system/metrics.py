from prometheus_client import Gauge, Counter, Histogram
import socket

SERVICE_NAME = 'alert_system'
NODE_NAME = socket.gethostname()

alerts_sent = Counter(
    'alerts_sent',
    'Number of alerts sent',
    ['service', 'node', 'alert_type'] # per distinguere tra "high_limit" e "low_limit"
)

alert_send_latency = Histogram(
    'alert_send_latency_seconds',
    'Duration of alert sending in seconds',
    ['service', 'node']
)

messages_consumed = Counter(
    'messages_consumed',
    'Number of messages consumed',
    ['service', 'node']
)

processing_errors = Counter(
    'processing_errors_total',
    'Total number of error during message processing',
    ['service', 'node']
)

messages_produced_for_notifications = Counter(
    'messages_produced_for_notifications_total',
    'Total number of messages produced for notifications',
    ['service', 'node']
)

delivery_failures = Counter(
    'delivery_failures',
    'Number of failed delivery attempts',
    ['service', 'node']
)