from sqlalchemy import func
import time
import logging
import yfinance as yf
from repositories import ticker_management_repository
from repositories import share_repository
from utils.circuit_breaker import CircuitBreaker, CBException, CBOpenException

circuit_breaker = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception)
logging = logging.getLogger(__name__)

def retrieve_share_value(share):
    msft = yf.Ticker(share)
    try:
        last_price = msft.info.get('currentPrice')
        if last_price is None:
            history = msft.history(period="1d", interval="1m")
            if not history.empty:
                last_price = history['Close'].iloc[-1]
            else:
                raise ValueError(f"No data available for ticker {share}")
    except Exception as e:
        print(f"Error retrieving data for {share}: {e}")
        last_price = None
    return last_price

def collect():
    tickers = ticker_management_repository.get_all_ticker_management()
    process_tickers(tickers, circuit_breaker)

def process_tickers(tickers, circuit_breaker):
    for ticker in tickers:
        if ticker.counter == 0:
            continue
        share = ticker.share_cod
        try:
            share_value = circuit_breaker.call(retrieve_share_value, share)
            if share_value is None:
                print(f"Could not retrieve share value for {share}. Skipping.")
                continue
        except CBOpenException as e:
            print("Circuit is open. Skipping call.")
        except CBException as e:
            print(f"Circuit breaker exception occurred: {e}")
        except Exception as e:
            print(f"Exception occurred: {e}")
        else:
            share_repository.create_share(share, float(share_value), func.now())
            print(f"Share value for {share}: {float(share_value)}")

def test_circuit_breaker_behavior():
    cb = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=5, expected_exception=ValueError)

    def simulate_success():
        return "Successo"

    def simulate_failure():
        raise ValueError("Errore")

    logging.error(f"Stato iniziale: {cb.state}")

    simulate_failures(cb, simulate_failure, 1, 5)
    simulate_successes(cb, simulate_success, 5, 6)
    simulate_failures(cb, simulate_failure, 6, 7)
    print(f"Stato dopo i fallimenti: {cb.state}")

    simulate_successes(cb, simulate_success, 7, 9)
    simulate_failures(cb, simulate_failure, 9, 11, CBOpenException)

    logging.info("Aspettando per passare in HALF_OPEN...")
    time.sleep(6)
    simulate_successes(cb, simulate_success, 11, 13)
    simulate_failures(cb, simulate_failure, 13, 14)
    simulate_successes(cb, simulate_success, 14, 16)
    simulate_failures(cb, simulate_failure, 16, 18)
    logging.info(f"Stato dopo i fallimenti: {cb.state}")

    logging.info("Aspettando per passare in HALF_OPEN...")
    time.sleep(6)
    simulate_successes(cb, simulate_success, 18, 22)
    simulate_failures(cb, simulate_failure, 22, 23)
    simulate_successes(cb, simulate_success, 23, 28)
    logging.info(f"Stato finale: {cb.state}")

def simulate_failures(cb, simulate_failure, start, end, exception_type=CBException):
    for i in range(start, end):
        try:
            cb.call(simulate_failure)
        except exception_type as e:
            logging.info(f"Chiamata {i} fallita: {e} - Stato: {cb.state}")

def simulate_successes(cb, simulate_success, start, end):
    for i in range(start, end):
        try:
            logging.info(f"Chiamata {i}: Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")
        except CBException as e:
            logging.info(f"Chiamata {i}: Errore durante il successo: {e}, Stato: {cb.state}")
