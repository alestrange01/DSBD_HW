import grpc
import services.homework1_pb2 as homework1_pb2
import services.homework1_pb2_grpc as homework1_pb2_grpc
import random
import re

target = 'localhost:50051'
logged_email = ""
password = ""

def run():
    while True:
        print("Running")
        print("Logged in as: ", logged_email)
        print("Choose an option:")
        print("0 - Update user")
        print("1 - Delete user")
        print("2 - Last value share")
        print("3 - Mean share")
        print("4 - Exit")
        
        choice = input("Inserisci la tua scelta: ")
        
        if choice == "0":
            update()
        elif choice == "1":
            print("Sei sicuro di voler eliminare il tuo account? ")
            print("0 - No")
            print("1 - Si")
            choice = input("Inserisci la tua scelta: ")
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
            print("Scelta non valida")

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
        print("6 - Test cache")
        print("7 - Exit")
        
        choice = input("Inserisci la tua scelta: ")
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
            test_cache()
        elif choice == "7":
            break
        else:
            print("Scelta non valida")
    
def update():
    share = input("Inserisci il tuo nuovo share d'interesse: ")
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.UpdateRequest(email=logged_email, share=share)
        metadata = [
            ('user_email', logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'PUT')
        ]
        try:
            response = stub.Update(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def admin_update():
    email = input("Inserisci l'email dell'utente da modificare: ")
    share = input("Inserisci il nuovo share d'interesse: ")
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.UpdateRequest(email=email, share=share)
        metadata = [
            ('user_email', logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'PUT')
        ]
        try:
            response = stub.Update(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def delete():  
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.DeleteRequest(email=logged_email)
        metadata = [
            ('user_email', logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'DEL')
        ]
        try:
            response = stub.Delete(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def admin_delete():
    email = input("Inserisci l'email dell'utente da eliminare: ")
    print("Sei sicuro di voler eliminare l'account dell'utente con email: ", email)
    print("0 - No")
    print("1 - Si")
    choice = input("Inserisci la tua scelta: ")
    if choice == "1":
        with grpc.insecure_channel(target) as channel:
            stub = homework1_pb2_grpc.ServerServiceStub(channel)
            request = homework1_pb2.DeleteRequest(email=email)
            metadata = [
                ('user_email', logged_email),
                ('request_id', str(random.randint(1, 1000))),
                ('op_code', 'DEL')
            ]
            try:
                response = stub.Delete(request, metadata=metadata)
                print("Response received: ", response)
            except grpc.RpcError as e:
                print(f"RPC failed with code {e.code()}: {e.details()}")
    else:
        print("Operazione annullata")

def get_value_share():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('user_email', logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.GetValueShare(request, metadata=metadata)
            print("Response received: ", response)
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
            ('user_email', logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.GetMeanShare(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def view_all_users():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('user_email', logged_email),
            ('request_id', str(random.randint(1, 1000))),
            ('op_code', 'GET')
        ]
        try:
            response = stub.ViewAllUsers(request, metadata=metadata)
            print("Response received: ", response)
            raw_content = response.content.split(": ", 1)[-1]
            users = parse_users(raw_content)
            print("\nLista degli utenti registrati:")
            for user in users:
                print(f"- ID: {user['id']}, Email: {user['email']}, Share: {user['share_cod']}")
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        except Exception as e:
            print(f"Error parsing users: {e}")

def parse_users(raw_content):
    try:
        start_index = raw_content.find("[")
        end_index = raw_content.find("]")
        users_raw = raw_content[start_index + 1 : end_index]
        users = []
        for user_raw in users_raw.split(", <User("):
            user_raw = user_raw.replace("<User(", "").replace(")>", "").strip()
            if not user_raw:
                continue
            user_dict = {}
            for field in user_raw.split(", "):
                key, value = field.split("=")
                user_dict[key.strip()] = value.strip().strip("'")
            users.append(user_dict)

        return users
    except Exception as e:
        print(f"Error parsing user data: {e}")
        return []




def login_or_register():
    choice = ""
    while choice != "0" and choice != "1":
        print("0 - Login")
        print("1 - Register")
        print("2 - Exit")
        choice = input("Inserisci la tua scelta: ")
        if choice == "0":
            login()
        elif choice == "1":
            register()
        elif choice == "2":
            exit()
        else:
            print("Scelta non valida")
             
def login(): 
    global logged_email
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
            print("Response received: ", response)
            if response.statusCode == 200:
                logged_email = email  
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        else:
            if response.statusCode == 200:
                if logged_email == "admin@gmail.com":
                    #ADMIN
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
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        else:
            if response.statusCode == 204:
                login()
            else:
                print("Registrazione fallita")

def admin_register_user(): 
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    while True:
        email = input("Inserisci la tua email: ")
        if re.match(email_pattern, email):
            break
        else:
            print("Formato email non valido. Riprova.")
    ruolo = input("Inserisci il ruolo: ")
    password = input("Inserisci la password: ")
    share = input("Inserisci il Ticker: ") 
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.RegisterRequest(email=email, password=password, role=ruolo, share=share)
        metadata = [
            ('user_email', email),
            ('request_id', str(random.randint(1, 1000))), 
            ('op_code', 'POST')
        ]
        try:
            response = stub.Register(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
        else:
            if response.statusCode == 204:
                login()
            else:
                print("Registrazione fallita")

def client_run():
    login_or_register()


def test_cache():
    max_num_retry = 3
    timeout = 8 
    retries = 0
    request_id = str(random.randint(1, 1000))

    while retries < max_num_retry:
        try:
            with grpc.insecure_channel(target) as channel:
                stub = homework1_pb2_grpc.ServerServiceStub(channel)
                metadata = [
                    ('user_email', logged_email), 
                    ('request_id', request_id),
                    ('op_code', 'GET')
                ]
                request = homework1_pb2.NoneRequest()
                response = stub.TestCache(request, timeout=timeout, metadata=metadata)
                print("Response received after", retries + 1, "retries: ", response.content)
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

#TODO: gesione errore canale chiuso dal server mentre il client è in attesa di una risposta