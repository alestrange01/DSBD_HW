from services.data_collector import collect
from db.db import initialize_database

if __name__ == '__main__':
    initialize_database()
    collect()