import random
import time
import re
import grpc
import services.homework1_pb2 as homework1_pb2
import services.homework1_pb2_grpc as homework1_pb2_grpc

target = 'localhost:50052'
INSERT_YOUR_CHOICE = "Inserisci la tua scelta: "
NOT_VALID_CHOICE = "Scelta non valida"
RESPONSE_RECEIVED = "Response received: "

class Session:
    def __init__(self):
        self.logged_email = None
        self.role = None

session = Session()

def client_run():
    login_or_register()

def login_or_register():
    choice = ""
    while choice != "0" and choice != "1":
        print("0 - Login")
        print("1 - Register")
        print("2 - Exit")
        choice = input(INSERT_YOUR_CHOICE)
        if choice == "0":
            login()
        elif choice == "1":
            register()
        elif choice == "2":
            exit()
        else:
            print(NOT_VALID_CHOICE)

def login(): 
    global session
    print("LOGIN:")
    email = input("Inserisci la tua email: ")
    password = input("Inserisci la tua password: ")
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.LoginRequest(email=email, password=password)
        metadata = [
            ('user_email', email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.Login(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        else:
            if response.statusCode == 200:
                session.logged_email = email
                session.role = response.role
                if session.role == "admin":
                    admin_run()
                else:
                    run()
            else:
                login_or_register()
            
def register(): 
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    while True:
        email = input("Inserisci la tua email: ")
        if re.match(email_pattern, email):
            break
        else:
            print("Formato email non valido. Riprova.")
    password = input("Inserisci la tua password: ")
    share = input("Inserisci il Ticker: ")
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.RegisterRequest(email=email, password=password, role="user", share=share)
        metadata = [
            ('user_email', email),
            ('request_id', str(random.randint(1, 1000))), 
            ('op_code', 'POST')
        ]
        try:
            response = stub.Register(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        else:
            if response.statusCode == 204:
                login()
            else:
                print("Registrazione fallita")

def run():
    while True:
        print("Running")
        print("Logged in as: ", session.logged_email)
        print("Choose an option:")
        print("0 - Update user")
        print("1 - Delete user")
        print("2 - Last value share")
        print("3 - Mean share")
        print("4 - Exit")
        
        choice = input(INSERT_YOUR_CHOICE)
        
        if choice == "0":
            update()
        elif choice == "1":
            print("Sei sicuro di voler eliminare il tuo account? ")
            print("0 - No")
            print("1 - Si")
            choice = input(INSERT_YOUR_CHOICE)
            if choice == "1":
                delete()
                break
            else:
                print("Operazione annullata")
        elif choice == "2":
            get_value_share()
        elif choice == "3":
            get_mean_share()
        elif choice == "4":
            break
        else:
            print(NOT_VALID_CHOICE)

def admin_run():
    while True:
        print("Running")
        print("Logged in as: ADMIN")
        print("Choose an option:")
        print("0 - Register a user")
        print("1 - Update user X")
        print("2 - Delete user X")
        print("3 - Last value share")
        print("4 - Mean share")
        print("5 - View all users")
        print("6 - View ticker management")
        print("7 - View all shares")
        print("8 - Test cache")
        print("9 - Exit")
        
        choice = input(INSERT_YOUR_CHOICE)
        if choice == "0":
            admin_register_user()
        elif choice == "1":
            admin_update()
        elif choice == "2":
            admin_delete()
        elif choice == "3":
            get_value_share()
        elif choice == "4":
            get_mean_share()
        elif choice == "5":
            view_all_users()
        elif choice == "6":
            view_ticker_management()
        elif choice == "7":
            view_all_shares()
        elif choice == "8":
            test_cache()
        elif choice == "9":
            break
        else:
            print(NOT_VALID_CHOICE)
    
def update():
    share = input("Inserisci il tuo nuovo share d'interesse: ")
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.UpdateRequest(email=session.logged_email, share=share)
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'PUT')
        ]
        try:
            response = stub.Update(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def delete():  
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.DeleteRequest(email=session.logged_email)
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'DEL')
        ]
        try:
            response = stub.Delete(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
            
def get_value_share():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.GetValueShare(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
def get_mean_share():
    while True:
        n = input("Inserisci il numero di share value da considerare: ")
        if not n.isdigit():
            print("Inserire un numero valido")
            continue
        if int(n) < 1:
            print("Inserire un numero maggiore di 0")
            continue
        break
    n = int(n)
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.MeanRequest(n=n)
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.GetMeanShare(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def admin_register_user(): 
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    while True:
        email = input("Inserisci l'email: ")
        if re.match(email_pattern, email):
            break
        else:
            print("Formato email non valido. Riprova.")
    while True:
        choice = input("Inserisci il ruolo: user (1) o admin (2): ") 
        if choice == "1":
            role = "user"
            break
        elif choice == "2":
            role = "admin"
            break
        else:
            print(NOT_VALID_CHOICE)
    password = input("Inserisci la password: ")
    share = input("Inserisci il Ticker: ") 
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.RegisterRequest(email=email, password=password, role=role, share=share)
        metadata = [
            ('user_email', email),
            ('request_id', str(random.randint(1, 1000))), 
            ('op_code', 'POST')
        ]
        try:
            response = stub.Register(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        else:
            if response.statusCode == 204:
                login()
            else:
                print("Registrazione fallita")
                
def admin_update():
    email = input("Inserisci l'email dell'utente da modificare: ")
    share = input("Inserisci il nuovo share d'interesse: ")
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.UpdateRequest(email=email, share=share)
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'PUT')
        ]
        try:
            response = stub.Update(request, metadata=metadata)
            print(RESPONSE_RECEIVED, response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def admin_delete():
    email = input("Inserisci l'email dell'utente da eliminare: ")
    print("Sei sicuro di voler eliminare l'account dell'utente con email: ", email)
    print("0 - No")
    print("1 - Si")
    choice = input(INSERT_YOUR_CHOICE)
    if choice == "1":
        with grpc.insecure_channel(target) as channel:
            stub = homework1_pb2_grpc.ServerServiceStub(channel)
            request = homework1_pb2.DeleteRequest(email=email)
            metadata = [
                ('user_email', session.logged_email),
                ('request_id', str(random.randint(1, 1000))),
                ('op_code', 'DEL')
            ]
            try:
                response = stub.Delete(request, metadata=metadata)
                print(RESPONSE_RECEIVED, response)
            except grpc.RpcError as e:
                print(f"RPC failed with code {e.code()}: {e.details()}")
    else:
        print("Operazione annullata")

def view_all_users():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.ViewAllUsers(request, metadata=metadata)
            print(f"Response received: status code {response.statusCode}, message {response.message}")
            users = parse(response.content, "User")
            print("\nLista degli utenti registrati:")
            for user in users:
                print(f"- ID: {user['id']}, Email: {user['email']}, Role: {user['role']}, Share: {user['share_cod']}")
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        except Exception as e:
            print(f"Error parsing users: {e}")

def view_ticker_management():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.ViewTickerManagement(request, metadata=metadata)
            print(f"Response received: status code {response.statusCode}, message {response.message}")
            ticker_managements = parse(response.content, "TickerManagement")
            print("\nTicker management:")
            for ticker_management in ticker_managements:
                print(f"- ID: {ticker_management['id']}, Share Cod: {ticker_management['share_cod']}, Counter: {ticker_management['counter']}")
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        except Exception as e:
            print(f"Error parsing ticker management: {e}")

def view_all_shares():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('user_email', session.logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.ViewAllShares(request, metadata=metadata)
            print(f"Response received: status code {response.statusCode}, message {response.message}")
            shares = parse(response.content, "Share")
            print("\nLista delle share:")
            for share in shares:
                print(f"- ID: {share['id']}, Share Cod: {share['share']}, Value: {share['value']}, Timestamp: {share['timestamp']}")
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        except Exception as e:
            print(f"Error parsing shares: {e}")

def test_cache():
    max_num_retry = 3
    timeout = 8 
    retries = 0
    request_id = str(random.randint(1, 1000))

    while retries < max_num_retry:
        try:
            start_time = time.time()
            with grpc.insecure_channel(target) as channel:
                stub = homework1_pb2_grpc.ServerServiceStub(channel)
                metadata = [
                    ('user_email', session.logged_email), 
                    ('request_id', request_id),
                    ('op_code', 'GET')
                ]
                request = homework1_pb2.NoneRequest()
                response = stub.TestCache(request, timeout=timeout, metadata=metadata)
                elapsed_time = time.time() - start_time
                print(f"Response received at {retries + 1} attempt after {elapsed_time:.5f} seconds: {response.content}")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print(f"Request timed out, retrying... ({retries + 1}/{max_num_retry})")
            else:
                print(f"RPC failed: {e}")
                break
        finally:
            retries += 1
    else:
        print("All retries done.")

def parse(raw_content, object_name):
    try:
        start_index = raw_content.find("[")
        end_index = raw_content.find("]")
        objects_raw = raw_content[start_index + 1:end_index]
        parsed_objects = []
        object_prefix = f"<{object_name}(" if "<" in objects_raw else f"{object_name}("
        
        for obj_raw in objects_raw.split(f", {object_prefix}"):
            obj_raw = obj_raw.replace(object_prefix, "").replace(")>", "").replace(")", "").strip()
            if not obj_raw:
                continue
            obj_dict = {}
            for field in obj_raw.split(", "):
                key, value = field.split("=")
                value = value.strip().strip("'")
                obj_dict[key.strip()] = value
            parsed_objects.append(obj_dict)
        
        return parsed_objects
    except Exception as e:
        print(f"Error parsing {object_name} data: {e}")
        return []

#TODO: gesione errore canale chiuso dal server mentre il client è in attesa di una risposta