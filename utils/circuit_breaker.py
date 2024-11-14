import time
import threading
from enum import Enum

class CircuitState(Enum):
    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    HALF_OPEN = 'HALF_OPEN'

class CircuitBreaker:
    def __init__(self, failure_threshold=5, difference_failure_open_half_open=2, success_threshold=5, recovery_timeout=30, expected_exception=Exception):
        self.failure_threshold = failure_threshold   
        self.difference_failure_open_half_open =  difference_failure_open_half_open
        self.success_threshold = success_threshold     
        self.recovery_timeout = recovery_timeout          
        self.expected_exception = expected_exception       
        self.failure_count = 0
        self.success_count = 0                             
        self.last_failure_time = None                      
        self.__set_state(CircuitState.CLOSED)                          
        self.lock = threading.Lock()                        

    def call(self, func, *args, **kwargs):
        with self.lock:
            if self.state == CircuitState.OPEN:
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure > self.recovery_timeout:
                    self.__set_state(CircuitState.HALF_OPEN)
                else:
                    raise CBOpenException("Call not allowed in OPEN state")
            try:
                result = func(*args, **kwargs)
            except self.expected_exception as e:
                self.__failure_management()
                raise CBException(e) 
            except Exception as e:
                self.__failure_management()
                raise e
            else:
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if (self.success_count >= self.success_threshold):
                        self.__set_state(CircuitState.CLOSED)
                return result  
            
    def __set_state(self, new_state):
        self.state = new_state
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
        #TODO: da aggiungere?
        #elif new_state == CircuitState.HALF_OPEN:
        #    self.failure_count = 0 
            
    def __failure_management(self):
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = time.time()                 
        if (self.state == CircuitState.HALF_OPEN) and (self.failure_count >= self.failure_threshold - self.difference_failure_open_half_open):
            self.__set_state(CircuitState.HALF_OPEN) #TODO: perchè aggiornare lo stato a HALF_OPEN se è già HALF_OPEN? forse dovrebbere essere OPEN?
        if (self.state == CircuitState.CLOSED) and (self.failure_count >= self.failure_threshold):
            self.__set_state(CircuitState.OPEN)
            
class CBException(Exception):
    print("Circuit breaker exception")

class CBOpenException(CBException):
    print("Circuit breaker open exception")
