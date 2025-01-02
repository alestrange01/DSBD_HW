from prometheus_client import Gauge, Counter, Histogram
import socket

SERVICE_NAME = 'data_collector'
NODE_NAME = socket.gethostname()

tickers_count = Gauge(
    'tickers_count', 
    'Number of tickers being monitored', 
    ['service', 'node']
)
 
yf_count = Counter(
    'yf_count', 
    'Number of yf call', 
    ['service', 'node']
)

yf_request_duration = Histogram(
    'yf_request_duration_seconds',
    'Duration of yfinance requests in seconds',
    ['service', 'node']
)
