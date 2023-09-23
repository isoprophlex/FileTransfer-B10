import argparse
import threading
from os import getpid, kill
from signal import SIGKILL
from socket import *
from utils import *



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


def start_server(args):

    logger = get_logger(args.verbose, args.quiet)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind((args.ADDR, args.PORT))
    logger.warning("Servidor iniciado")


if __name__ == '__main__':
    start_server(get_args())
