import random
import time
import yfinance as yf
from utils.circuit_breaker import CircuitBreaker, CBException, CBOpenException
from repositories import user_repository
from repositories import share_repository
from sqlalchemy import func

def retrieve_share_value(share):
    msft = yf.Ticker(share)
    last_price = msft.info['currentPrice']
    return last_price


def collect():
    circuit_breaker = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception)
    share_dict = {}
    while True:
        users = user_repository.get_all_users()
        for user in users:
            share = user.share_cod
            if(share in share_dict):
                share_repository.create_share(user.id, share, share_dict[share], func.now())
                continue
            try:
                share_value = circuit_breaker.call(retrieve_share_value, share)
            except CBOpenException as e:
                print(f"Circuit is open. Skipping call.")
            except CBException as e:
                print(f"Circuit breaker exception occurred: {e}")
            except Exception as e:
                print(f"Exception occurred: {e}")
            else:
                share_dict[share] = share_value
            share_repository.create_share(user.id, share, share_dict[share], func.now())
            print(f"Share value for {share}: {share_value}")
        share_dict= {} 
        time.sleep(300)

