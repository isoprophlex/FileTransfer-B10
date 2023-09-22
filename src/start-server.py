import argparse
import threading
from os import getpid, kill
from signal import SIGKILL
from socket import *
import utils

import click
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


def main(verbose, quiet, host, port, storage):
    logger = utils.get_logger(verbose, quiet)
    print("Ingrese la letra q para finalizar el servidor")
    server_socket = socket(AF_INET, SOCK_DGRAM)
    logger.info("Socket abierto del lado del servidor")
    server_socket.bind((host, port))
    logger.warning("Servidor iniciado")
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


        except KeyboardInterrupt:
    logger.info("Server cerrado")
    pid = getpid()
    kill(pid, SIGKILL)
    exit_thread.join()



if __name__ == '__main__':
    main()