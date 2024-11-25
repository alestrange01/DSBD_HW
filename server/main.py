from db.db import initialize_database
from services.server import serve, start_cleaner_thread

if __name__ == '__main__':
    initialize_database()
    start_cleaner_thread()
    serve()
    