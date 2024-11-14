import random
import time
import yfinance as yf
from utils.circuit_breaker import CircuitBreaker, CBException, CBOpenException
from ..repositories import user_repository
from ..repositories import share_repository
from sqlalchemy import func

def retrieve_share_value(share):
    msft = yf.Ticker(share)
    last_price = msft.info['regularMarketPrice']
    # data = stock.history(period="1d")
    # last_price = data['Close'].iloc[-1] 
    return last_price

circuit_breaker = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception)
share_dict = {}
while True:
    users = user_repository.get_all_users()
    for user in range(users):
        #prendo lo share value dell'utente
        share = user.share_int
        if(share_dict[share]):
            share_repository.create_share(user.id, share, share_dict[share], func.now())
            break
        try:
            share_value = circuit_breaker.call(retrieve_share_value)
        except CBOpenException as e:
            print(f"Call {i+1}: Circuit is open. Skipping call.")
        except CBException as e:
            print(f"Call {i+1}: Circuit is open. Skipping call.")
        except Exception as e:
            print(f"Call {i+1}: Exception occurred - {e}")
        share_dict[share] = share_value
        share_repository.create_share(user.id, share, share_dict[share], func.now())
        print(f"Call {i+1}: {share_value}")
    share_dict= {}
    time.sleep(300)

