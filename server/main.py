from services.server import serve
from db.db import initialize_database

if __name__ == '__main__':
    initialize_database()
    serve()
    