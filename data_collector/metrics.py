import prometheus_client
import socket

HOSTNAME = socket.gethostname()
APP_NAME = "data_collector_exporter" 

tickers_count = prometheus_client.Gauge(
    'tickers_count', 
    'Fake response time', #che vuo dire fake response time?
    ['server', 'hostname', 'app']
)
 
# Prometheus Counter metric for number of iterations, with server, hostname, and app as labels
yf_count = prometheus_client.Counter(
    'yf_count', 
    'Real iterations value', 
    ['server', 'hostname', 'app']
)

yf_request_duration = prometheus_client.Histogram(
    'yf_request_duration_seconds',
    'Duration of yfinance requests in seconds',
    ['server', 'hostname', 'app']
)
