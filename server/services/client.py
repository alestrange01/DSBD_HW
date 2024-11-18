import grpc
import services.homework1_pb2 as homework1_pb2
import services.homework1_pb2_grpc as homework1_pb2_grpc
import random
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
            delete()
        elif choice == "2":
            get_value_share()
        elif choice == "3":
            get_mean_share()
        elif choice == "4":
            break
        else:
            print("Scelta non valida")
    
def update():
    share = input("Inserisci il tuo nuovo share d'interesse: ")
    # Valutare se rimuovere un ticker o sostituirlo obbligatoriamente con un altro
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.UpdateRequest(email=logged_email, share=share)
        metadata = [
            ('userid', logged_email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 'PUT')
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
            ('userid', logged_email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 'DEL')
        ]
        try:
            response = stub.Delete(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
def get_value_share():
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.NoneRequest()
        metadata = [
            ('userid', logged_email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 'GET')
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
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.MeanRequest(n=n)
        metadata = [
            ('userid', logged_email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 'GET')
        ]
        try:
            response = stub.GetMeanShare(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

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
    email = input("Inserisci la tua email: ")
    password = input("Inserisci la tua password: ")
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.LoginRequest(email=email, password=password)
        metadata = [
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 'GET')
        ]
        try:
            response = stub.Login(request, metadata=metadata)
            print("Response received: ", response)
            if response.statusCode == "200":
                logged_email = email  
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
            
def register(): 
    email = input("Inserisci la tua email: ")
    password = input("Inserisci la tua password: ")
    share = input("Inserisci il Ticker: ")
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.RegisterRequest(email=email, password=password, share=share)
        metadata = [
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 'POST')
        ]
        try:
            response = stub.Register(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def client_run():
    login_or_register()
    run()