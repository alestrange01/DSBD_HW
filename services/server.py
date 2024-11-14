from concurrent import futures
import logging
import grpc
import homework1_pb2
import homework1_pb2_grpc
import time
import bcrypt
from threading import Lock
from ..db import db
from ..repositories import user_repository
from ..repositories import share_repository

request_cache = []

cache_lock = Lock()

class ServerService(homework1_pb2_grpc.ServerServiceServicer):

    def Login(self, request, context): 
        user_id, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_id, request_id, op_code)
        if cached_response is not None:
            print("Login cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            if (user is None) or (not bcrypt.checkpw(request.password.encode('utf-8'), user.password)):
                response = homework1_pb2.Reply(statusCode=401, message="Unauthorized", content="Login failed")
                print("Login failed")
                return response
            else:
                response = homework1_pb2.Reply(statusCode=200, message="OK", content="Login successful")
                self.__StoreInCache(user_id, request_id, op_code, response)
                print("Login")
                return response
    
    def Register(self, request, context):        
        user_id, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_id, request_id, op_code)
        if cached_response is not None:
            print("Register cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            if user is not None:
                response = homework1_pb2.Reply(statusCode=401, message="Unauthorized", content="User registration failed")
                print("Register failed")
                return response
            else:
                hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
                user_repository.create_user(request.email, hashed_password, request.share)
                response = homework1_pb2.Reply(statusCode=204, message="OK", content="User registered successfully")
                self.__StoreInCache(user_id, request_id, op_code, response)
                print("Register")
                return response
    
    def Update(self, request, context):        
        user_id, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_id, request_id, op_code)
        if cached_response is not None:
            print("Update cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            if user is not None:
                response = homework1_pb2.Reply(statusCode=401, message="Unauthorized", content="User updating failed")
                print("Update failed")
                return response
            else:
                user_repository.update_user(request.email, None, request.share) #TODO: vorresti aggiornare anche la password?
                share_repository.delete_shares_by_user(user.id)
                response = homework1_pb2.Reply(statusCode=201, message="OK", content="User updated successfully")
                self.__StoreInCache(user_id, request_id, op_code, response)
                print("Update")
                return response

    def Delete(self, request, context):        
        user_id, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_id, request_id, op_code)
        if cached_response is not None:
            print("Delete cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            if user is not None:
                response = homework1_pb2.Reply(statusCode=401, message="Unauthorized", content="User deleting failed")
                print("Delete failed")
                return response
            else:
                user_repository.delete_user(user.email)
                share_repository.delete_shares_by_user(user.id)
                response = homework1_pb2.Reply(statusCode=201, message="OK", content="User deleted successfully")
                self.__StoreInCache(user_id, request_id, op_code, response)
                print("Delete")
                return response
        
    def GetValueShare(self, request, context):
        user_id, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_id, request_id, op_code)
        if cached_response is not None:
            print("Get value share cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            shares = share_repository.get_shares_by_user_id(user.id)
            if shares is None:
                response = homework1_pb2.Reply(statusCode=404, message="Bad request", content="Retrieve value share failed")
                print("Get value share failed")
                return response
            else:
                last_share = shares[-1]
                response = homework1_pb2.Reply(statusCode=200, message="OK", content="Retrieved value share successfully: " + str(last_share.value))
                self.__StoreInCache(user_id, request_id, op_code, response)
                print("Get value share")
                return response
    
    def GetValueShare(self, request, context):
        user_id, request_id, op_code = self.__GetMetadata(context)
        cached_response = self.__GetFromCache(user_id, request_id, op_code)
        if cached_response is not None:
            print("Get mean share cached response")
            return cached_response
        else:
            user = user_repository.get_user_by_email(request.email)
            shares = share_repository.get_shares_by_user_id(user.id)
            if shares is None:
                response = homework1_pb2.Reply(statusCode=404, message="Bad request", content="Retrieve mean share failed")
                print("Get value share failed")
                return response
            else:
                mean = sum([share.value for share in shares]) / len(shares)
                response = homework1_pb2.Reply(statusCode=200, message="OK", content="Retrieved mean share successfully: " + str(mean))
                self.__StoreInCache(user_id, request_id, op_code, response)
                print("Get mean share")
                return response

    def __GetMetadata(self, context): 
        meta = dict(context.invocation_metadata())
        print(meta)
        user_id = meta.get('userid', 'unknown')   
        request_id = meta.get('requestid', 'unknown')  
        op_code = meta.get('opcode', 'unknown') 
        return user_id, request_id, op_code

    def __GetFromCache(self, user_id, request_id, op_code):
        user_request_id = user_id + "_" + request_id
        with cache_lock:
            if user_request_id in request_cache[op_code]:
                print(f"Returning cached response for RequestID {request_id}")
                return request_cache[op_code][user_request_id]
            else:
                return None
            
    def __StoreInCache(self, user_id, request_id, op_code, response):
        user_request_id = user_id + "_" + request_id + "_" + op_code
        with cache_lock:
            request_cache[op_code][user_request_id] = response


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    homework1_pb2_grpc.add_ServerServiceServicer_to_server(ServerService(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Echo Service started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    db.initialize_database() 
    
    serve()
