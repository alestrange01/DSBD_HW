from concurrent import futures
import re
import time
import bcrypt
from threading import Lock
import grpc
import services.homework1_pb2 as homework1_pb2
import services.homework1_pb2_grpc as homework1_pb2_grpc
from repositories import user_repository
from repositories import share_repository
from repositories import ticker_management_repository


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
            print("Login cached response")
            return cached_response
        else:
            print(request)
            user = user_repository.get_user_by_email(request.email)
            print(user)
            if (user is None) or (not bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8'))):
                response = homework1_pb2.LoginReply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Login failed: wrong email or password", role="unknown")
                print("Login failed")
                return response
            else:
                print("Login successful")
                response = homework1_pb2.LoginReply(statusCode=200, message=OK_MESSAGE, content="Login successful", role=user.role)
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("Login")
                return response
    

    def Register(self, request, context):        
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("Register cached response")
            return cached_response
        else:
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, request.email):
                print("Invalid email format")
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Invalid email format")
                return response
            else:
                user = user_repository.get_user_by_email(request.email)
                if user is not None:
                    response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User registration failed")
                    print("Register failed")
                    return response
                else:
                    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    user_repository.create_user(email=request.email, password=hashed_password, share_cod=request.share, role=request.role)
                    ticker_management = ticker_management_repository.get_ticker_management_by_code(request.share)
                    if ticker_management is None:
                        ticker_management_repository.create_ticker_management(request.share)
                    else:
                        ticker_management_repository.update_ticker_management(request.share, ticker_management.counter + 1)
                    response = homework1_pb2.Reply(statusCode=204, message=OK_MESSAGE, content="User registered successfully")
                    self.__StoreInCache(user_email, request_id, op_code, response)
                    print("Register")
                    return response
    
    def Update(self, request, context):        
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("Update cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            if user is None or not self.__IsAuthorized(request.email, user_email):
                response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User updating failed")
                print("Update failed")
                return response
            else:
                if request.share == user.share_cod:
                    content = "Share already updated"
                else:  
                    user_repository.update_user(request.email, None, request.share) #TODO: vorresti aggiornare anche la password?
                    old_ticker_management = ticker_management_repository.get_ticker_management_by_code(user.share_cod)
                    ticker_management_repository.update_ticker_management(user.share_cod, old_ticker_management.counter - 1)
                    new_ticker_management = ticker_management_repository.get_ticker_management_by_code(request.share)
                    if new_ticker_management is None:
                        ticker_management_repository.create_ticker_management(request.share)
                    else:
                        ticker_management_repository.update_ticker_management(request.share, new_ticker_management.counter + 1)
                    content = "User updated successfully"

                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=content)
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("Update")
                return response

    def Delete(self, request, context):        
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("Delete cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            if user is None or not self.__IsAuthorized(request.email, user_email):
                response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User deleting failed")
                print("Delete failed")
                return response
            else:     
                user_repository.delete_user(user.email)
                ticker_management = ticker_management_repository.get_ticker_management_by_code(user.share_cod)
                ticker_management_repository.update_ticker_management(user.share_cod, ticker_management.counter - 1)
                response = homework1_pb2.Reply(statusCode=201, message=OK_MESSAGE, content="User deleted successfully")
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("Delete")
                return response
        
    def GetValueShare(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("Get value share cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(user_email)
            share_name = user.share_cod
            share = share_repository.get_latest_share_by_name(share_name)
            if share is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve value share failed")
                print("Get value share failed")
                return response
            else:
                #TODO: Può richiederlo un admin o ognuno il suo?
                print(share)
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content="Retrieved value share successfully: " + str(share.value))
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("Get value share")
                return response
    
    def GetMeanShare(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("Get mean share cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(user_email)
            share_name = user.share_cod
            shares = share_repository.get_shares_by_share_name(share_name)
            if shares is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve mean share failed")
                print("Get value share failed")
                return response
            else:
                #TODO: Può richiederlo un admin o ognuno il suo?
                try:
                    n = int(request.n)
                    if n < 1:
                        raise ValueError("Invalid n")
                except ValueError:
                    response = homework1_pb2.Reply(statusCode=400, message=BAD_REQUEST_MESSAGE, content="Invalid value for n")
                    print("Invalid value for n")
                    return response
                limited_shares = shares[:n] if len(shares) > n else shares
                mean = sum([share.value for share in limited_shares]) / len(limited_shares)
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content="Retrieved mean share successfully: " + str(mean))
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("Get mean share")
                return response
            
    def ViewAllUsers(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)

        if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
            response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view all users")
            print("View all users failed.")
            return response

        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("View all users cached response")
            return cached_response
        else:
            users = user_repository.get_all_users()
            if users is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve all users failed")
                print("View all users failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=str(users))
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("View all users")
                return response

    def ViewTickerManagement(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)

        if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
            response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view ticker management")
            print("View ticker management failed.")
            return response

        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("View ticker management cached response")
            return cached_response
        else:
            ticker_management = ticker_management_repository.get_all_ticker_management()
            if ticker_management is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve ticker management failed")
                print("View ticker management failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=str(ticker_management))
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("View ticker management")
                return response
    
    def ViewAllShares(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)

        if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
            response = homework1_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view all shares")
            print("View all shares failed.")
            return response

        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("View all shares cached response")
            return cached_response
        else:
            shares = share_repository.get_all_shares()
            if shares is None:
                response = homework1_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve all shares failed")
                print("View all shares failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=str(shares))
                self.__StoreInCache(user_email, request_id, op_code, response)
                print("View all shares")
                return response
            
    def TestCache(self, request, context):
        user_email, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_email, request_id, op_code)
        if cached_response is not None:
            print("Returning cached response")
            del request_attempts[request_id]
            return cached_response

        if request_id not in request_attempts:
            request_attempts[request_id] = 0
        
        request_attempts[request_id] += 1
        attempt_count = request_attempts[request_id]

        if attempt_count == 1:
            print(f"Simulating delay for attempt {attempt_count}")
            time.sleep(10) 
        elif attempt_count == 2:
            print(f"Simulating delay for attempt {attempt_count}")
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
        print(meta)
        user_email = meta.get('user_email', 'unknown')   
        request_id = meta.get('request_id', 'unknown')  
        op_code = meta.get('op_code', 'unknown') 
        return user_email, request_id, op_code

    def __GetFromCache(self, user_email, request_id, op_code):
        print(f"Checking cache for RequestID {request_id}")
        user_request_id = user_email + "_" + request_id
        with cache_lock:
            if user_request_id in request_cache[op_code]:
                print(f"Returning cached response for RequestID {request_id}")
                return request_cache[op_code][user_request_id]
            else:
                print(f"No cached response for RequestID {request_id}")
                return None
            
    def __StoreInCache(self, user_email, request_id, op_code, response):
        user_request_id = user_email + "_" + request_id
        with cache_lock:
            request_cache[op_code][user_request_id] = response

    def __IsAuthorized(self, request_email, user_email, required_role=None):
        logged_user = user_repository.get_user_by_email(user_email)
        if required_role and logged_user.role != required_role:
            return False
        return request_email == user_email or logged_user.role == "admin"

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    homework1_pb2_grpc.add_ServerServiceServicer_to_server(ServerService(), server)
    server.add_insecure_port('[::]:' + port)
    
    try:
        server.start()
        print(f"Server started, listening on port {port}")
        server.wait_for_termination() 
    except KeyboardInterrupt:
        print("Server interrupted by user.")
    finally:
        server.stop(0)  
        print("Server stopped.")
