from decimal import Decimal
import logging
import re
import bcrypt
from db.db import DB
from dto.user import UserCreationDTO, UserUpdateDTO
from dto.ticker_management import TickerManagementUpsertDTO
from repositories.user_repository_reader import UserRepositoryReader
from repositories.user_repository_writer import UserRepositoryWriter
from repositories.ticker_management_repository_reader import TickerManagementRepositoryReader
from repositories.ticker_management_repository_writer import TickerManagementRepositoryWriter

BAD_REQUEST_MESSAGE = "Bad request"
UNOTHORIZED_MESSAGE = "Unauthorized"
OK_MESSAGE = "OK"

logging = logging.getLogger(__name__)

class RegisterCommand:
    def __init__(self, request):
        ticker_management_repository_reader = TickerManagementRepositoryReader(DB())
        ticker_management_repository_writer = TickerManagementRepositoryWriter(DB())
        user_repository_reader = UserRepositoryReader(DB())
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_pattern, request.email):
            logging.error("Invalid email format")
            raise ValueError("Invalid email format")
        else:
            user = user_repository_reader.get_user_by_email(request.email)
            if user is not None:
                logging.error("User already exists")
                raise ValueError("User already exists")
            else:
                request_high_value = Decimal(request.highValue) if request.HasField("highValue") else None
                request_low_value = Decimal(request.lowValue) if request.HasField("lowValue") else None
                hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                self.email = request.email
                self.password = hashed_password
                self.share = request.share
                self.role = request.role
                self.high_value = request_high_value
                self.low_value = request_low_value
                ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(request.share) #TODO Non query perchè non ha logica?
                if ticker_management is None:
                    ticker_management_repository_writer.create_ticker_management(TickerManagementUpsertDTO(request.share, 1)) #TODO Non command perchè non ha logica o bisogna crearlo?
                else:
                    ticker_management_repository_writer.update_ticker_management(TickerManagementUpsertDTO(request.share, ticker_management.counter + 1)) #TODO Non command perchè non ha logica o bisogna crearlo?
                logging.info("Register")
                
class UpdateCommand:
    def __init__(self, request, user_email):
        ticker_management_repository_reader = TickerManagementRepositoryReader(DB())
        ticker_management_repository_writer = TickerManagementRepositoryWriter(DB())
        user_repository_reader = UserRepositoryReader(DB())        
        user = user_repository_reader.get_user_by_email(request.email)
        if user is None:
            raise ValueError("User does not exist")
        request_high_value = Decimal(request.highValue) if request.HasField("highValue") else None
        request_low_value = Decimal(request.lowValue) if request.HasField("lowValue") else None
        if request.share == user.share_cod and self.compare_values(request_high_value, user.high_value) and self.compare_values(request_low_value, user.low_value):
            self.content = False
        else:
            self.email = request.email
            self.share = request.share
            self.high_value = request_high_value
            self.low_value = request_low_value
            self.password = None
            
            if request.share != user.share_cod:
                old_ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(user.share_cod)
                ticker_management_repository_writer.update_ticker_management(TickerManagementUpsertDTO(user.share_cod, old_ticker_management.counter - 1))
                new_ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(request.share)
                if new_ticker_management is None:
                    ticker_management_repository_writer.create_ticker_management(TickerManagementUpsertDTO(request.share, 1))
                else:
                    ticker_management_repository_writer.update_ticker_management(TickerManagementUpsertDTO(request.share, new_ticker_management.counter + 1))
            logging.info("Update")
            self.content = True

    def compare_values(self, value1, value2):
        if value1 is None and value2 is None:
            return True
        if value1 is not None and value2 is not None:
            return Decimal(value1) == Decimal(value2)
        return False

class DeleteCommand():
    def __init__(self, request):
        ticker_management_repository_reader = TickerManagementRepositoryReader(DB())
        ticker_management_repository_writer = TickerManagementRepositoryWriter(DB())
        user_repository_reader = UserRepositoryReader(DB())
        user = user_repository_reader.get_user_by_email(request.email)  
        if user is None:
            raise ValueError("User does not exist")
        self.email = user.email
        ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(user.share_cod)
        ticker_management_repository_writer.update_ticker_management(TickerManagementUpsertDTO(user.share_cod, ticker_management.counter - 1))
        logging.info("Delete")

class UserWriteService:
    def __init__(self):
        self.db = DB()
        self.user_repository_writer = UserRepositoryWriter(self.db)
        
    def handle_register_user(self, command: RegisterCommand):
        user_creation_dto = UserCreationDTO(command.email, command.password, command.role, command.share, command.high_value, command.low_value)
        user = self.user_repository_writer.create_user(user_creation_dto= user_creation_dto)
        logging.info("User created: {user}")
    
    def handle_update_user(self, command: UpdateCommand):
        if command.content:
            user_update_dto = UserUpdateDTO(command.email, command.share, command.high_value, command.low_value)
            self.user_repository_writer.update_user(user_update_dto)
            logging.info("User updated: {user}")
            return "User updated successfully"
        else:
            return "User already has this share and values"
    
    def handle_delete_user(self, command: DeleteCommand):
        self.user_repository_writer.delete_user(command.email)
        logging.info("User deleted: {user}")