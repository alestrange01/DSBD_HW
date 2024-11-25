from sqlalchemy import func
import time
import yfinance as yf
from repositories import user_repository
from repositories import share_repository
from utils.circuit_breaker import CircuitBreaker, CBException, CBOpenException

circuit_breaker = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception)

def retrieve_share_value(share):
    msft = yf.Ticker(share)
    last_price = msft.info['currentPrice']
    return last_price

def collect():
    share_dict = {}
    users = user_repository.get_all_users()
    process_users(users, share_dict, circuit_breaker)

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

def test_circuit_breaker_behavior():
    cb = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=5, expected_exception=ValueError)

    def simulate_success():
        return "Successo"

    def simulate_failure():
        raise ValueError("Errore")

    print(f"Stato iniziale: {cb.state}")

    simulate_failures(cb, simulate_failure, 1, 5)
    print(f"Chiamata 5: {cb.call(simulate_success)} - Stato: {cb.state}")

    try:
        cb.call(simulate_failure)
    except CBException as e:
        print(f"Chiamata 6 fallita: {e} - Stato: {cb.state}")

    print(f"Stato dopo i fallimenti: {cb.state}")
    simulate_successes(cb, simulate_success, 7, 9)
    simulate_failures(cb, simulate_failure, 9, 11, CBOpenException)

    print("Aspettando per passare in HALF_OPEN...")
    time.sleep(6)
    simulate_successes(cb, simulate_success, 11, 13)

    try:
        cb.call(simulate_failure)
    except CBException as e:
        print(f"Chiamata 13 fallita: {e} - Stato: {cb.state}")

    simulate_successes(cb, simulate_success, 14, 16)
    simulate_failures(cb, simulate_failure, 16, 18)

    print(f"Stato dopo i fallimenti: {cb.state}")

    print("Aspettando per passare in HALF_OPEN...")
    time.sleep(6)
    simulate_successes(cb, simulate_success, 19, 23)

    try:
        cb.call(simulate_failure)
    except CBException as e:
        print(f"Chiamata 23 fallita: {e} - Stato: {cb.state}")

    simulate_successes(cb, simulate_success, 24, 29)

    print(f"Stato finale: {cb.state}")

def simulate_failures(cb, simulate_failure, start, end, exception_type=CBException):
    for i in range(start, end):
        try:
            cb.call(simulate_failure)
        except exception_type as e:
            print(f"Chiamata {i} fallita: {e} - Stato: {cb.state}")

def simulate_successes(cb, simulate_success, start, end):
    for i in range(start, end):
        try:
            print(f"Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")
        except CBException as e:
            print(f"Errore durante il successo: {e}, Stato: {cb.state}")
