import argparse
import FileReader
from socket import *

from src.utils import get_logger


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
        "-s", "--dst", dest="FILEPATH",
        required=True, help="source file path", action="store", type=str
    )
    parser.add_argument(
        "-n", "--name", dest="FILENAME",
        required=True, help="file name", action="store", type=str
    )
    return parser.parse_args()

def upload(verbose, quiet, host, port, src, name):
    logger = get_logger(verbose, quiet)
    print("Ingrese la letra q para finalizar la subida del archivo: ")
    client_socket = socket(AF_INET, SOCK_DGRAM)

    file_name = f"{src}/{name}"
    logger.warning("Cliente listo para subir un archivo")

    reader = FileReader(file_name)

    file_size = reader.get_file_size()
    # Definir MAX_FILE_SIZE
    if file_size > MAX_FILE_SIZE:
        logger.error("El tamaño del archivo es muy grande")
        return