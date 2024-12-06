import logging
from concurrent import futures
import re
import time
import bcrypt
from threading import Lock
from decimal import Decimal
import grpc
import services.homework1_pb2 as homework1_pb2
import services.homework1_pb2_grpc as homework1_pb2_grpc
from server.repositories import user_repository_reader, user_repository_writer
from server.repositories import share_repository_reader
from server.repositories import ticker_management_repository_reader, ticker_management_repository_writer

logging = logging.getLogger(__name__)

request_cache = {'GET': {}, 'POST': {}, 'PUT': {}, 'DEL': {}}
request_attempts = {}
cache_lock = Lock()
BAD_REQUEST_MESSAGE = "Bad request"
UNOTHORIZED_MESSAGE = "Unauthorized"
OK_MESSAGE = "OK"

class ServerService(homework1_pb2_grpc.ServerServiceServicer):
    def Login(self, request, context): 
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Login cached response")
            return cached_response
        else:
            logging.info(request)
            user = user_repository_reader.get_user_by_email(request.email)
            logging.info(user)
            if (user is None) or (not bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8'))):
                response = homework1_pb2.LoginReply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Login failed: wrong email or password", role="unknown")
                logging.error("Login failed")
                return response
            else:
                logging.info("Login successful")
                response = homework1_pb2.LoginReply(statusCode=200, message=OK_MESSAGE, content="Login successful", role=user.role)
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("Login")
                return response
    

    def Register(self, request, context):        
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Register cached response")
            return cached_response
        else:
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, request.email):
                logging.error("Invalid email format")
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Invalid email format")
                return response
            else:
                user = user_repository_reader.get_user_by_email(request.email)
                if user is not None:
                    response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User registration failed")
                    logging.error("Register failed")
                    return response
                else:
                    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    user_repository_writer.create_user(email=request.email, password=hashed_password, share_cod=request.share, role=request.role, high_value=Decimal(request.high_value), low_value=Decimal(request.low_value))
                    ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(request.share)
                    if ticker_management is None:
                        ticker_management_repository_writer.create_ticker_management(request.share)
                    else:
                        ticker_management_repository_writer.update_ticker_management(request.share, ticker_management.counter + 1)
                    response = homework1_pb2.Reply(statusCode=204, message=OK_MESSAGE, content="User registered successfully")
                    self.__StoreInCache(user_email, request_id, op_code, response)
                    logging.info("Register")
                    return response
    
    def Update(self, request, context):        
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Update cached response")
            return cached_response
        else:
            user = user_repository_reader.get_user_by_email(request.email)
            if user is None or not self.__IsAuthorized(request.email, user_email):
                response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User updating failed")
                logging.error("Update failed")
                return response
            else:
                if request.share == user.share_cod:
                    content = "Share already updated"
                else:  
                    user_repository_writer.update_user(request.email, None, request.share, Decimal(request.high_value), Decimal(request.low_value))
                    old_ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(user.share_cod)
                    ticker_management_repository_writer.update_ticker_management(user.share_cod, old_ticker_management.counter - 1)
                    new_ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(request.share)
                    if new_ticker_management is None:
                        ticker_management_repository_writer.create_ticker_management(request.share)
                    else:
                        ticker_management_repository_writer.update_ticker_management(request.share, new_ticker_management.counter + 1)
                    content = "User updated successfully"

                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=content)
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("Update")
                return response

    def Delete(self, request, context):        
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Delete cached response")
            return cached_response
        else:
            user = user_repository_reader.get_user_by_email(request.email)
            if user is None or not self.__IsAuthorized(request.email, user_email):
                response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User deleting failed")
                logging.error("Delete failed")
                return response
            else:     
                user_repository_writer.delete_user(user.email)
                ticker_management = ticker_management_repository_reader.get_ticker_management_by_code(user.share_cod)
                ticker_management_repository_writer.update_ticker_management(user.share_cod, ticker_management.counter - 1)
                response = homework1_pb2.Reply(statusCode=201, message=OK_MESSAGE, content="User deleted successfully")
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("Delete")
                return response
        
    def GetValueShare(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Get value share cached response")
            return cached_response
        else:
            user = user_repository_reader.get_user_by_email(user_email)
            share_name = user.share_cod
            share = share_repository_reader.get_latest_share_by_name(share_name)
            if share is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve value share failed")
                logging.error("Get value share failed")
                return response
            else:
                logging.info(share)
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content="Retrieved "+ str(share_name) + " value successfully: " + str(share.value))
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("Get value share")
                return response
    
    def GetMeanShare(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Get mean share cached response")
            return cached_response
        else:
            user = user_repository_reader.get_user_by_email(user_email)
            share_name = user.share_cod
            shares = share_repository_reader.get_shares_by_share_name(share_name)
            if shares is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve mean share failed")
                logging.error("Get value share failed")
                return response
            else:
                try:
                    n = int(request.n)
                    if n < 1:
                        raise ValueError("Invalid n")
                except ValueError:
                    response = homework1_pb2.Reply(statusCode=400, message=BAD_REQUEST_MESSAGE, content="Invalid value for n")
                    logging.error("Invalid value for n")
                    return response
                limited_shares = shares[:n] if len(shares) > n else shares
                mean = sum([share.value for share in limited_shares]) / len(limited_shares)
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content="Mean value of " + str(share_name) + " of " + str(len(limited_shares)) + " latest shares: " + "{:.3f}".format(mean))
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("Get mean share")
                return response
            
    def ViewAllUsers(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)

        if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
            response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view all users")
            logging.error("View all users failed.")
            return response

        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("View all users cached response")
            return cached_response
        else:
            users = user_repository_reader.get_all_users()
            if users is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve all users failed")
                logging.error("View all users failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=str(users))
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("View all users")
                return response

    def ViewTickerManagement(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)

        if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
            response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view ticker management")
            logging.error("View ticker management failed.")
            return response

        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("View ticker management cached response")
            return cached_response
        else:
            ticker_management = ticker_management_repository_reader.get_all_ticker_management()
            if ticker_management is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve ticker management failed")
                logging.error("View ticker management failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=str(ticker_management))
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("View ticker management")
                return response
    
    def ViewAllShares(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)

        if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
            response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view all shares")
            logging.error("View all shares failed.")
            return response

        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("View all shares cached response")
            return cached_response
        else:
            shares = share_repository_reader.get_all_shares()
            if shares is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve all shares failed")
                logging.error("View all shares failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=str(shares))
                self.__StoreInCache(user_email, request_id, op_code, response)
                logging.info("View all shares")
                return response
            
    def TestAtMostOncePolicy(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            logging.info("Returning cached response")
            del request_attempts[request_id]
            return cached_response

        if request_id not in request_attempts:
            request_attempts[request_id] = 0
        
        request_attempts[request_id] += 1
        attempt_count = request_attempts[request_id]

        if attempt_count == 1:
            logging.info(f"Simulating delay for attempt {attempt_count}")
            time.sleep(10) 
        elif attempt_count == 2:
            logging.info(f"Simulating delay for attempt {attempt_count}")
            time.sleep(5)

        response = homework1_pb2.Reply(
            statusCode=200,
            message="Processed successfully",
            content=f"Hello {user_email}, your request {request_id} has been processed."
        )
        self.__StoreInCache(user_email, request_id, op_code, response)
        return response

    def __GetMetadata(self, context): 
        meta = dict(context.invocation_metadata())
        logging.info(meta)
        user_email = meta.get('user_email', 'unknown')   
        request_id = meta.get('request_id', 'unknown')  
        op_code = meta.get('op_code', 'unknown') 
        return user_email, request_id, op_code

    def __GetFromCache(self, user_email, request_id, op_code):
        logging.info(f"Checking cache for RequestID {request_id}")
        user_request_id = user_email + "_" + request_id
        with cache_lock:
            if user_request_id in request_cache[op_code]:
                logging.info(f"Returning cached response for RequestID {request_id}")
                return request_cache[op_code][user_request_id]['response']
            else:
                logging.info(f"No cached response for RequestID {request_id}")
                return None

            
    def __StoreInCache(self, user_email, request_id, op_code, response):
        user_request_id = user_email + "_" + request_id
        with cache_lock:
            request_cache[op_code][user_request_id] = {'response': response, 'timestamp': time.time()}

    def __IsAuthorized(self, request_email, user_email, required_role=None):
        logged_user = user_repository_reader.get_user_by_email(user_email)
        if required_role and logged_user.role != required_role:
            return False
        return request_email == user_email or logged_user.role == "admin"
    

def clean_cache():
    current_time = time.time()
    threshold = 120
    logging.info("Pulizia cache...")
    logging.info("Cache attuale:")
    logging.info(request_cache)
    with cache_lock:
        for op_code in request_cache:
            keys_to_delete = [
                key for key, value in request_cache[op_code].items()
                if current_time - value['timestamp'] > threshold
            ]
            for key in keys_to_delete:
                del request_cache[op_code][key]
    logging.info("Cache dopo pulizia:")
    logging.info(request_cache)

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    homework1_pb2_grpc.add_ServerServiceServicer_to_server(ServerService(), server)
    server.add_insecure_port('[::]:' + port)
    
    try:
        server.start()
        logging.info(f"Server started, listening on port {port}")
        server.wait_for_termination() 
    except KeyboardInterrupt:
        logging.info("Server interrupted by user.")
    finally:
        server.stop(0)  
        logging.info("Server stopped.")
