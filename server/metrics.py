from prometheus_client import Gauge, Counter, Histogram
import socket

SERVICE_NAME = 'server'
NODE_NAME = socket.gethostname()

users = Gauge(
    'users_total',
    'Total number of users',
    ['service', 'node']
)

requests = Counter(
    'requests_total',
    'Total number of requests',
    ['service', 'node', 'method', 'response_type']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Duration of requests to the server, in seconds',
    ['service', 'node', 'method']
)
 
errors = Counter(
    'errors_total',
    'Total number of errors, categorized by method and error type',
    ['service', 'node', 'method', 'status_code']
)

cache_size = Gauge(
    'cache_size',
    'Current size of the cache',
    ['service', 'node']
)