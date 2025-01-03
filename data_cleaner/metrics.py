from prometheus_client import Gauge, Counter, Histogram
import socket

SERVICE_NAME = 'data_cleaner'
NODE_NAME = socket.gethostname()

shares_deleted = Counter(
    'shares_deleted',
    'Number of shares deleted',
    ['service', 'node', 'reason']
)

ticker_management_deleted = Counter(
    'ticker_management_deleted',
    'Number of ticker management deleted',
    ['service', 'node']
)

cleaning_request_duration = Histogram(
    'cleaning_request_duration_seconds',
    'Duration of cleaning requests in seconds',
    ['service', 'node']
)

old_shares_ratio = Gauge(
    'old_shares_ratio',
    'Percentage of shares deleted because they were old',
    ['service', 'node'] 
)

