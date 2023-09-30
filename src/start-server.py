import argparse
import threading
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
        try:
            input_value = input()
        except EOFError:
            break
        if input_value == "q":
            try:
                socket.close()
            except:
                break
            for thread in threads:
                thread.join()
            for connection in connections:
                connection.close_file_reader()
            break


def start_server(args):
    logger = get_logger(args.verbose, args.quiet)
    logger.setLevel(args.verbose)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind((args.ADDR, args.PORT))
    logger.info("Server started...")
    threads = []
    connections = []
    exit_thread = threading.Thread(
        target=is_finishing, args=(server_socket, threads, connections)
    )
    exit_thread.start()
    server_socket.setblocking(False)
    while True:
        try:
            if not exit_thread.is_alive():
                logger.info("Cerrando servidor")
                break

            client_data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            if not client_data:
                continue
            new_thread_list = []
            for thread in threads:
                if thread.is_alive():
                    new_thread_list.append(thread)

            threads = new_thread_list
            if len(threads) >= MAX_CLIENTS_CONNECTED:
                logger.info(
                    "Se alcanzó el máximo de clientes conectados al mismo tiempo"
                )
                continue

            new_connection = ClientManager(client_address, client_data.decode(), args.verbose, args.quiet, args.FILEPATH)
            connections.append(new_connection)
            new_thread = new_connection.connect()
            new_thread.start()
            logger.warning(f"Se ha conectado un nuevo cliente: {client_address}")
        except BlockingIOError:
            continue
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt: Server shutting down...")
            for thread in threads:
                thread.join()
            exit_thread.join()
            try:
                server_socket.close()
            except Exception as e:
                logger.error(f"Error while closing server socket: {e}")

if __name__ == '__main__':
    start_server(get_args())
