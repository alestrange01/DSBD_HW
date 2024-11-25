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




import time

def test_circuit_breaker_behavior():
    cb = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=5, expected_exception=ValueError)

    def simulate_success():
        return "Successo"

    def simulate_failure():
        raise ValueError("Errore")

    print(f"Stato iniziale: {cb.state}")

    #simulo fallimenti
    for i in range(1,5):
        try:
            cb.call(simulate_failure)
        except CBException as e:
            print(f"Chiamata {i} fallita: {e} - Stato: {cb.state}")

    print(f"Chiamata {i+1}: {cb.call(simulate_success)} - Stato: {cb.state}")   

    try:
        cb.call(simulate_failure)
    except CBException as e:
        print(f"Chiamata {i+2} fallita: {e} - Stato: {cb.state}")

    #verifico lo stato OPEN
    print(f"Stato dopo i fallimenti: {cb.state}")
    for i in range(7,9):
        try:
            print(f"Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")
        except CBException as e:
            print(f"Errore durante il successo: {e}, Stato: {cb.state}")

    for i in range(9,11):
        try:
            cb.call(simulate_failure)
        except CBOpenException as e:
            print(f"Chiamata bloccata: {e} - Stato: {cb.state}")

    #aspetto per passare in HALF_OPEN
    print("Aspettando per passare in HALF_OPEN...")
    time.sleep(6)  #recovery timeout + 1 cosi' da superare il recovery timeout
    for i in range(11,13):
        try:
            cb.call(simulate_success)
        except CBOpenException as e:
            print(f"Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")   
    
    try:
        cb.call(simulate_failure)
    except CBException as e:
        print(f"Chiamata {i+1} fallita: {e} - Stato: {cb.state}")
    
    for i in range(14,16):
        try:
            cb.call(simulate_success)
        except CBOpenException as e:
            print(f"Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")   

    for i in range(16,18):
        try:
            cb.call(simulate_failure)
        except CBException as e:
            print(f"Chiamata {i} fallita: {e} - Stato: {cb.state}")

    #verifico lo stato OPEN
    print(f"Stato dopo i fallimenti: {cb.state}")

    print("Aspettando per passare in HALF_OPEN...")
    time.sleep(6)
    #simulo successi
    for i in range(19,23):
        try:
            print(f"Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")
        except CBException as e:
            print(f"Errore inatteso durante il successo: {e}")

    try:
        cb.call(simulate_failure)
    except CBException as e:
        print(f"Chiamata {i+1} fallita: {e} - Stato: {cb.state}")
    
    for i in range(24,29):
        try:
            print(f"Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")
        except CBException as e:
            print(f"Errore inatteso durante il successo: {e}")

    #stato finale
    print(f"Stato finale: {cb.state}")
