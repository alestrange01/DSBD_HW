import argparse
from app.client import client_run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for the gRPC server.")
    parser.add_argument("port", type=int, help="Port number of the gRPC server")
    args = parser.parse_args()

    client_run(port=args.port)
