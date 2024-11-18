import grpc
import homework1_pb2
import homework1_pb2_grpc
import random
target = 'localhost:50051'
email = ""
password = ""

def run():
    while True:
        print("Running")
        print("Logged in as: ", email)
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
        request = homework1_pb2.UpdateRequest(email=email, share=share)
        metadata = [
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 2)
        ]
        try:
            response = stub.Update(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")
def delete():  
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.DeleteRequest(email=email)
        metadata = [
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 2)
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
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 3)
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
        request = homework1_pb2.MeanRequest(n = n)
        metadata = [
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 4)
        ]
        try:
            response = stub.GetMeanShare(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

def login_or_register():
    while True:
        print("0 - Login")
        print("1 - Register")
        print("2 - Exit")
        choice = input("Inserisci la tua scelta: ")
        if choice == "0":
            login()
        elif choice == "1":
            register()
        elif choice == "2":
            break
        else:
            print("Scelta non valida")
             
def login(): 
    email = input("Inserisci la tua email: ")
    password = input("Inserisci la tua password: ")
    
    with grpc.insecure_channel(target) as channel:
        stub = homework1_pb2_grpc.ServerServiceStub(channel)
        request = homework1_pb2.LoginRequest(email=email, password=password)
        metadata = [
            ('userid', email),
            ('requestid', str(random.randint(1, 1000))),
            ('opcode', 0)
        ]
        try:
            response = stub.Login(request, metadata=metadata)
            print("Response received: ", response)
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
            ('opcode', 1)
        ]
        try:
            response = stub.Register(request, metadata=metadata)
            print("Response received: ", response)
        except grpc.RpcError as e:
            print(f"RPC failed with code {e.code()}: {e.details()}")

if __name__ == '__main__':
    login_or_register()
    run()