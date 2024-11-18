from services.server import serve
from services.data_collector import collect
from db.db import initialize_database
import threading

if __name__ == '__main__':
    initialize_database()
    serve()
    threading.Thread(target=collect).start()