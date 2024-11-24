from sqlalchemy import func
import time
import yfinance as yf
from repositories import user_repository
from repositories import share_repository
from utils.circuit_breaker import CircuitBreaker, CBException, CBOpenException

def retrieve_share_value(share):
    msft = yf.Ticker(share)
    last_price = msft.info['currentPrice']
    return last_price

def collect():
    circuit_breaker = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception)
    while True:
        share_dict = {}
        users = user_repository.get_all_users()
        process_users(users, share_dict, circuit_breaker)
        time.sleep(300)

def process_users(users, share_dict, circuit_breaker):
    for user in users:
        share = user.share_cod
        if share in share_dict:
            print(f"Share value for {share}: {share_dict[share]} already retrieved.")
            continue
        try:
            share_value = circuit_breaker.call(retrieve_share_value, share)
        except CBOpenException as e:
            print("Circuit is open. Skipping call.")
        except CBException as e:
            print(f"Circuit breaker exception occurred: {e}")
        except Exception as e:
            print(f"Exception occurred: {e}")
        else:
            share_dict[share] = share_value
            share_repository.create_share(share, share_dict[share], func.now())
            print(f"Share value for {share}: {share_value}")
