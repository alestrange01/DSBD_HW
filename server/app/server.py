from threading import Lock
from concurrent import futures
import logging
import json
import time
import grpc
import app.homework2_pb2 as homework2_pb2
import app.homework2_pb2_grpc as homework2_pb2_grpc
from services.user_write_service import RegisterCommand, UpdateCommand, DeleteCommand, UserWriteService
from services.user_reader_service import UserReaderService
from services.ticker_management_reader_service import TickerManagementReaderService
from services.share_reader_service import ShareReaderService
from metrics import users, requests , login_request_duration, register_request_duration, update_request_duration, delete_request_duration, view_all_users_request_duration, view_ticker_management_request_duration, view_all_shares_request_duration, get_value_share_request_duration, get_mean_share_request_duration, test_at_most_once_policy_request_duration, SERVICE_NAME, NODE_NAME

logging = logging.getLogger(__name__)

request_cache = {'GET': {}, 'POST': {}, 'PUT': {}, 'DEL': {}}
request_attempts = {}
cache_lock = Lock()
BAD_REQUEST_MESSAGE = "Bad request"
UNOTHORIZED_MESSAGE = "Unauthorized"
OK_MESSAGE = "OK"

class Server(homework2_pb2_grpc.ServerServicer):
    def __init__(self):
        pass
            
    def Login(self, request, context): 
        with login_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Login", response_type="cached").inc()
                logging.info("Login cached response")
                return cached_response
            else:
                try:
                    user_reader_service = UserReaderService()
                    content, role = user_reader_service.login(request)
                    response = homework2_pb2.LoginReply(statusCode=200, message=OK_MESSAGE, content=content, role=role)
                except ValueError as e:
                    response = homework2_pb2.LoginReply(statusCode=401, message=BAD_REQUEST_MESSAGE, content=str(e), role="unknown")
                except Exception as e:
                    response = homework2_pb2.LoginReply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e), role="unknown")
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, response)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Login", response_type="processed").inc()
                return response
    

    def Register(self, request, context):   
        with register_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():   
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Register", response_type="cached").inc()
                logging.info("Register cached response")
                return cached_response
            else:
                try:
                    user_write_service = UserWriteService()
                    user_write_service.handle_register_user(RegisterCommand(request))
                    message = homework2_pb2.Reply(statusCode=204, message=OK_MESSAGE, content="User registered successfully")
                except ValueError as e:
                    message = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    message = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, message)
                    users.labels(service=SERVICE_NAME, node=NODE_NAME).inc()
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Register", response_type="processed").inc()
                return message
    
    def Update(self, request, context):  
        with update_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():      
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Update", response_type="cached").inc()
                logging.info("Update cached response")
                return cached_response
            if not self.__IsAuthorized(request.email, user_email):
                response = homework2_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User updating failed")
                logging.error("Update failed")
                return response
            else:
                try:
                    user_write_service = UserWriteService()
                    content = user_write_service.handle_update_user(UpdateCommand(request, user_email))
                    message = homework2_pb2.Reply(statusCode=204, message=OK_MESSAGE, content=content)
                except ValueError as e:
                    message = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    message = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, message)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Update", response_type="processed").inc()
                return message

    def Delete(self, request, context):      
        with delete_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Delete", response_type="cached").inc()
                logging.info("Delete cached response")
                return cached_response
            if not self.__IsAuthorized(request.email, user_email):
                response = homework2_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="User updating failed")
                logging.error("Update failed")
                return response
            else:
                try:
                    user_write_service = UserWriteService()
                    user_write_service.handle_delete_user(DeleteCommand(request=request))
                    message = homework2_pb2.Reply(statusCode=204, message=OK_MESSAGE, content="User deleted successfully")
                except ValueError as e:
                    message = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    message = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, message)     
                    users.labels(service=SERVICE_NAME, node=NODE_NAME).dec()
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="Delete", response_type="processed").inc()
                return message
            
    def ViewAllUsers(self, request, context):
        with view_all_users_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)

            if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
                response = homework2_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view all users")
                logging.error("View all users failed.")
                return response

            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="ViewAllUsers", response_type="cached").inc()
                logging.info("View all users cached response")
                return cached_response
            else:
                try:
                    user_reader_service = UserReaderService()
                    users = user_reader_service.get_all_users()
                    response_content = json.dumps([user.to_dict() for user in users])
                    response = homework2_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=response_content)
                except ValueError as e:
                    response = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    response = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:   
                    self.__StoreInCache(user_email, request_id, op_code, response)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="ViewAllUsers", response_type="processed").inc()
                return response

    def ViewTickerManagement(self, request, context):
        with view_ticker_management_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)

            if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
                response = homework2_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view ticker management")
                logging.error("View ticker management failed.")
                return response

            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="ViewTickerManagement", response_type="cached").inc()
                logging.info("View ticker management cached response")
                return cached_response
            else:
                try:
                    ticker_management_reader_service = TickerManagementReaderService()
                    ticker_managements = ticker_management_reader_service.get_all_ticker_managements()
                    response_content = json.dumps([ticker_management.to_dict() for ticker_management in ticker_managements])
                    response = homework2_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=response_content)
                except ValueError as e:
                    response = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    response = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, response)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="ViewTickerManagement", response_type="processed").inc()
                return response
                
    def ViewAllShares(self, request, context):
        with view_all_shares_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)

            if not self.__IsAuthorized(request_email=None, user_email=user_email, required_role="admin"):
                response = homework2_pb2.Reply(statusCode=401, message=UNOTHORIZED_MESSAGE, content="Only admin can view all shares")
                logging.error("View all shares failed.")
                return response

            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="ViewAllShares", response_type="cached").inc()
                logging.info("View all shares cached response")
                return cached_response
            else:
                try:
                    share_reader_service = ShareReaderService()
                    shares = share_reader_service.get_all_shares()
                    logging.info(f"Shares: {shares}")
                    response_content = json.dumps([share.to_dict() for share in shares])
                    response = homework2_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=response_content)
                except ValueError as e:
                    response = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    response = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, response)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="ViewAllShares", response_type="processed").inc()
                return response
            
    def GetValueShare(self, request, context):
        with get_value_share_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="GetValueShare", response_type="cached").inc()
                logging.info("Get value share cached response")
                return cached_response
            else:
                try:
                    share_reader_service = ShareReaderService()
                    share = share_reader_service.get_values_share(user_email)
                    response = homework2_pb2.Reply(statusCode=200, message=OK_MESSAGE, content="Value of " + str(share.share_name) + " share: " + "{:.3f}".format(share.value))
                except ValueError as e:
                    response = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content="Retrieve share failed")
                    logging.error("Get value share failed")
                except Exception as e:
                    response = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, response)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="GetValueShare", response_type="processed").inc()
                return response
    
    def GetMeanShare(self, request, context):
        with get_mean_share_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="GetMeanShare", response_type="cached").inc()
                logging.info("Get mean share cached response")
                return cached_response
            else:
                try:
                    share_reader_service = ShareReaderService()
                    content = share_reader_service.get_mean_share(request, user_email)
                    response = homework2_pb2.Reply(statusCode=200, message=OK_MESSAGE, content=content)
                except ValueError as e:
                    response = homework2_pb2.Reply(statusCode=404, message=BAD_REQUEST_MESSAGE, content=str(e))
                except Exception as e:
                    response = homework2_pb2.Reply(statusCode=500, message=BAD_REQUEST_MESSAGE, content=str(e))
                finally:
                    self.__StoreInCache(user_email, request_id, op_code, response)
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="GetMeanShare", response_type="processed").inc()
                return response
            
    def TestAtMostOncePolicy(self, request, context):
        with test_at_most_once_policy_request_duration.labels(service=SERVICE_NAME, node=NODE_NAME).time():
            user_email, request_id, op_code = self.__GetMetadata(context)
            cached_response = self.__GetFromCache(user_email, request_id, op_code)
            if cached_response is not None:
                requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="TestAtMostOncePolicy", response_type="cached").inc()
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

            response = homework2_pb2.Reply(
                statusCode=200,
                message="Processed successfully",
                content=f"Hello {user_email}, your request {request_id} has been processed."
            )
            self.__StoreInCache(user_email, request_id, op_code, response)
            requests.labels(service=SERVICE_NAME, node=NODE_NAME, method="TestAtMostOncePolicy", response_type="processed").inc()
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
        logging.info("Contenuto della cache:\n%s", json.dumps(request_cache, indent=4, default=str))
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
        user_reader_service = UserReaderService()
        logged_user = user_reader_service.get_user_by_email(user_email)
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
    logging.info("\nCache dopo pulizia:")
    logging.info(request_cache)

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    homework2_pb2_grpc.add_ServerServicer_to_server(Server(), server)
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
