import logging
from concurrent import futures
import re
import time
import bcrypt
from decimal import Decimal
import grpc
import services.homework1_pb2 as homework1_pb2
import services.homework1_pb2_grpc as homework1_pb2_grpc
from server.repositories import user_repository_writer
from server.repositories import ticker_management_repository_reader, ticker_management_repository_writer
from server.services.user_reader_service import UserReaderService
from db.db import get_db_session

BAD_REQUEST_MESSAGE = "Bad request"
UNOTHORIZED_MESSAGE = "Unauthorized"
OK_MESSAGE = "OK"

class RegisterCommand:
    def __init__(self, request):
        user_reader_service = UserReaderService(get_db_session())
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_pattern, request.email):
            logging.error("Invalid email format")
            raise ValueError("Invalid email format")
        else:
            user = user_reader_service.get_user_by_email(request.email)
            if user is not None:
                logging.error("User already exists")
                raise ValueError("User already exists")
            else:
                hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                self.email = request.email
                self.password = hashed_password
                self.share = request.share
                self.role = request.role
                self.high_value = Decimal(request.high_value)
                self.low_value = Decimal(request.low_value)
                ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(request.share) #TODO Non query perchè non ha logica?
                if ticker_management is None:
                    ticker_management_repository_writer.create_ticker_management(request.share) #TODO Non command perchè non ha logica o bisogna crearlo?
                else:
                    ticker_management_repository_writer.update_ticker_management(request.share, ticker_management.counter + 1) #TODO Non command perchè non ha logica o bisogna crearlo?
                logging.info("Register")

class UserWriteService:
    def __init__(self):
        pass

    def handle_register_user(self, command: RegisterCommand):
        user = user_repository_writer.create_user(email=command.email, password=command.password, share_cod=command.share, role=command.role, high_value=command.high_value, low_value=command.low_value)
        print(user) 