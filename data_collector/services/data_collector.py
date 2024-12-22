from sqlalchemy import func
from confluent_kafka import Producer
import logging
import time
import yfinance as yf
import json
from db.db import DB
from dto.share import ShareCreationDTO
from repositories.ticker_management_repository_reader import TickerManagementRepositoryReader
from repositories.share_repository_writer import ShareRepositoryWriter
from utils.circuit_breaker import CircuitBreaker, CBException, CBOpenException

logging = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        producer_config = {
            'bootstrap.servers': 'kafka-broker:9092',  
            'acks': 'all',  
            'batch.size': 500,  
            'max.in.flight.requests.per.connection': 1,      
            'retries': 3  
        }
        self.producer = Producer(producer_config)
        self.topic = "to-alert-system"

        self.circuit_breaker = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception)
        self.db = DB()
        self.ticker_management_repository_reader = TickerManagementRepositoryReader(self.db)
        self.share_repository_writer = ShareRepositoryWriter(self.db)
        
    def collect(self):
        tickers = self.ticker_management_repository_reader.get_all_ticker_management()
        self.__process_tickers(tickers, self.circuit_breaker)

    def __process_tickers(self, tickers, circuit_breaker):
        for ticker in tickers:
            if ticker.counter == 0:
                continue
            share = ticker.share_cod
            try:
                share_value = circuit_breaker.call(self.__retrieve_share_value, share)
                if share_value is None:
                    logging.info(f"Could not retrieve share value for {share}. Skipping.")
                    continue
            except CBOpenException as e:
                logging.error("Circuit is open. Skipping call.")
            except CBException as e:
                logging.error(f"Circuit breaker exception occurred: {e}")
            except Exception as e:
                logging.error(f"Exception occurred: {e}")
            else:
                share_dto = ShareCreationDTO(share, share_value, func.now())
                self.share_repository_writer.create_share(share_dto)
                logging.info(f"Share value for {share}: {float(share_value)}")
        
        message = {"msg" : "Share value updated"}
        self.producer.produce(self.topic, json.dumps(message), callback=self.__delivery_report)
        self.producer.flush() 
        print(f"Produced: {message}")
        
    def __retrieve_share_value(self, share):
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
            logging.error(f"Error retrieving data for {share}: {e}")
            last_price = None
        return last_price
        
    def __delivery_report(self, err, msg):
        if err:
            print(f"Delivery failed: {err}, retrying...")
            
            message = {"msg" : "Share value updated"}    
            self.producer.produce(self.topic, json.dumps(message), callback=self.__delivery_report)
            self.producer.flush()
            print(f"Produced: {message}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    def test_circuit_breaker_behavior(self):
        cb = CircuitBreaker(failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=5, expected_exception=ValueError)

        def simulate_success():
            return "Successo"

        def simulate_failure():
            raise ValueError("Errore")

        logging.info(f"Stato iniziale: {cb.state}")

        self.simulate_failures(cb, simulate_failure, 1, 5)
        self.simulate_successes(cb, simulate_success, 5, 6)
        self.simulate_failures(cb, simulate_failure, 6, 7)
        logging.info(f"Stato dopo i fallimenti: {cb.state}")

        self.simulate_successes(cb, simulate_success, 7, 9)
        self.simulate_failures(cb, simulate_failure, 9, 11, CBOpenException)

        logging.info("Aspettando per passare in HALF_OPEN...")
        time.sleep(6)
        self.simulate_successes(cb, simulate_success, 11, 13)
        self.simulate_failures(cb, simulate_failure, 13, 14)
        self.simulate_successes(cb, simulate_success, 14, 16)
        self.simulate_failures(cb, simulate_failure, 16, 18)
        logging.info(f"Stato dopo i fallimenti: {cb.state}")

        logging.info("Aspettando per passare in HALF_OPEN...")
        time.sleep(6)
        self.simulate_successes(cb, simulate_success, 18, 22)
        self.simulate_failures(cb, simulate_failure, 22, 23)
        self.simulate_successes(cb, simulate_success, 23, 28)
        logging.info(f"Stato finale: {cb.state}")

    def simulate_failures(self, cb, simulate_failure, start, end, exception_type=CBException):
        for i in range(start, end):
            try:
                cb.call(simulate_failure)
            except exception_type as e:
                logging.error(f"Chiamata {i} fallita: {e} - Stato: {cb.state}")

    def simulate_successes(self, cb, simulate_success, start, end):
        for i in range(start, end):
            try:
                logging.info(f"Chiamata {i}: Risultato: {cb.call(simulate_success)} - Stato: {cb.state}")
            except CBException as e:
                logging.error(f"Chiamata {i}: Errore durante il successo: {e}, Stato: {cb.state}")
