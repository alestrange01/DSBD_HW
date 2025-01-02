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

login_request_duration = Histogram(
    'login_request_duration_seconds',
    'Duration of login requests in seconds',
    ['service', 'node']
)
 
register_request_duration = Histogram(
    'register_request_duration_seconds',
    'Duration of register requests in seconds',
    ['service', 'node']
)

update_request_duration = Histogram(
    'update_request_duration_seconds',
    'Duration of update requests in seconds',
    ['service', 'node']
)

delete_request_duration = Histogram(
    'delete_request_duration_seconds',
    'Duration of delete requests in seconds',
    ['service', 'node']
)

view_all_users_request_duration = Histogram(
    'view_all_users_request_duration_seconds',
    'Duration of view all users requests in seconds',
    ['service', 'node']
)

view_ticker_management_request_duration = Histogram(
    'view_ticker_management_request_duration_seconds',
    'Duration of view ticker management requests in seconds',
    ['service', 'node']
)

view_all_shares_request_duration = Histogram(
    'view_all_shares_request_duration_seconds',
    'Duration of view all shares requests in seconds',
    ['service', 'node']
)

get_value_share_request_duration = Histogram(
    'get_value_share_request_duration_seconds',
    'Duration of get value share requests in seconds',
    ['service', 'node']
)

get_mean_share_request_duration = Histogram(
    'get_mean_share_request_duration_seconds',
    'Duration of get mean share requests in seconds',
    ['service', 'node']
)

test_at_most_once_policy_request_duration = Histogram(
    'test_at_most_once_policy_request_duration_seconds',
    'Duration of test at most once policy requests in seconds',
    ['service', 'node']
)