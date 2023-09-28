import argparse
from multiprocessing import Process
from os import getpid, kill
# from signal import SIGKILL
from socket import *
from utils import *
from constants import *
from ClientManager import *


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbose",
        required=False, help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet",
        required=False, help="decrease output verbosity", action="store_true"
    )
    parser.add_argument(
        "-H", "--host", dest="ADDR",
        required=True, help="server IP address", action="store", type=str
    )
    parser.add_argument(
        "-p", "--port", dest="PORT",
        required=True, help="server port", action="store", type=int
    )
    parser.add_argument(
        "-s", "--storage", dest="FILEPATH",
        required=True, help="storage dir path", action="store", type=str
    )
    return parser.parse_args()


def is_finishing(socket, threads, connections):
    while True:
        input_value = input()
        if input_value == "q":
            try:
                socket.close()
            except:
                break
            for thread in threads:
                thread.join()
            for connection in connections:
                connection.close_file_manager()
            break


def handle_client(client_address, client_data, args):
    new_connection = ClientManager(client_address, client_data.decode(), args.verbose, args.quiet, args.FILEPATH)
    new_connection.accept_connection()
    new_connection.close_file_reader()

def start_server(serve_args):
    proccesses = []
    logger = get_logger(serve_args.verbose, serve_args.quiet)
    logger.warning("Server started...")
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind((serve_args.ADDR, serve_args.PORT))
    try:
        while True:
            client_data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            logger.warning(f"client_data: {client_data} - client_address: {client_address}")
            new_process = Process(target=handle_client, args=(client_address, client_data, serve_args))
            new_process.start()
            proccesses.append(new_process)
            logger.warning(f"Se ha conectado un nuevo cliente: {client_address}")
    except KeyboardInterrupt:
        for proccess in proccesses:
            proccess.join()


if __name__ == '__main__':
    start_server(get_args())
