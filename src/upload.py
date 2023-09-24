import argparse
from FileReader import *
from socket import *
from Intro.src.lib.constants import *
from src.utils import *
from lib.constants import *

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


def upload(args):
    logger = get_logger(args.verbose, args.quiet)
    print("Ingrese la letra q para finalizar la subida del archivo: ")
    client_socket = socket(AF_INET, SOCK_DGRAM)

    file_name = f"{args.FILEPATH}/{args.FILENAME}"
    logger.warning("Cliente listo para subir un archivo")

    reader = FileReader(file_name)

    file_size = reader.get_file_size()

    if file_size > MAX_FILE_SIZE:
        logger.error("El tamaño del archivo es muy grande")
        return

    hipoteticas_cosas_que_salen_de_handshake, result = handshake_upload(
        file_name, file_size, reader, client_socket, args.ADDR, args.PORT, sel_repeat, logger
    )

    # if result is False:
        #return

    # if sel_repeeat is True:
    #    upload_type = SelectiveRepeat()
    #    logger.info("File is uploading with Selective Repeat protocol")
    #else:
    #    upload_type = StopAndWait()
    #    logger.info("File is uploading with Stop&Wait protocol")

    #upload_type.upload_file(
     #   client_socket, hipoteticas_cosas_que_salen_de_handshake, reader, logger
    #)

#def handshake_upload(
        #file_name, file_size, reader, client_socket, args.ADDR, args.PORT, sel_repeat, logger
    #)
upload(get_args())
