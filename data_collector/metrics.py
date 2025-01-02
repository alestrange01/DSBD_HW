import prometheus_client
import socket

SERVICE_NAME = 'data_collector'
NODE_NAME = socket.gethostname()

tickers_count = prometheus_client.Gauge(
    'tickers_count', 
    'Number of tickers being monitored', 
    ['service', 'node']
)
 
yf_count = prometheus_client.Counter(
    'yf_count', 
    'Number of yf call', 
    ['service', 'node']
)

yf_request_duration = prometheus_client.Histogram(
    'yf_request_duration_seconds',
    'Duration of yfinance requests in seconds',
    ['service', 'node']
)
