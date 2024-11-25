from db.db import initialize_database
from services.data_collector import collect, test_circuit_breaker_behavior

if __name__ == '__main__':
    initialize_database()
    #collect()
    test_circuit_breaker_behavior()