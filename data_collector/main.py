from db.db import initialize_database
from services.data_collector import collect

if __name__ == '__main__':
    initialize_database()
    collect()