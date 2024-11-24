from db.db import initialize_database
from services.server import serve

if __name__ == '__main__':
    initialize_database()
    serve()
    