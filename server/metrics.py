import prometheus_client
import socket

SERVICE_NAME = 'data_collector'
NODE_NAME = socket.gethostname()

users = prometheus_client.Gauge(
    'users_total',
    'Total number of users',
    ['service', 'node']
)

requests = prometheus_client.Counter(
    'requests_total',
    'Total number of requests',
    ['service', 'node', 'method']
)

login_request_duration = prometheus_client.Histogram(
    'login_request_duration_seconds',
    'Duration of login requests in seconds',
    ['service', 'node']
)
 
register_request_duration = prometheus_client.Histogram(
    'register_request_duration_seconds',
    'Duration of register requests in seconds',
    ['service', 'node']
)

update_request_duration = prometheus_client.Histogram(
    'update_request_duration_seconds',
    'Duration of update requests in seconds',
    ['service', 'node']
)

delete_request_duration = prometheus_client.Histogram(
    'delete_request_duration_seconds',
    'Duration of delete requests in seconds',
    ['service', 'node']
)

view_all_users_request_duration = prometheus_client.Histogram(
    'view_all_users_request_duration_seconds',
    'Duration of view all users requests in seconds',
    ['service', 'node']
)

view_ticker_management_request_duration = prometheus_client.Histogram(
    'view_ticker_management_request_duration_seconds',
    'Duration of view ticker management requests in seconds',
    ['service', 'node']
)

view_all_shares_request_duration = prometheus_client.Histogram(
    'view_all_shares_request_duration_seconds',
    'Duration of view all shares requests in seconds',
    ['service', 'node']
)

get_value_share_request_duration = prometheus_client.Histogram(
    'get_value_share_request_duration_seconds',
    'Duration of get value share requests in seconds',
    ['service', 'node']
)

get_mean_share_request_duration = prometheus_client.Histogram(
    'get_mean_share_request_duration_seconds',
    'Duration of get mean share requests in seconds',
    ['service', 'node']
)

test_at_most_once_policy_request_duration = prometheus_client.Histogram(
    'test_at_most_once_policy_request_duration_seconds',
    'Duration of test at most once policy requests in seconds',
    ['service', 'node']
)