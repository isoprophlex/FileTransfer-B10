import argparse
import time

from FileReader import *
from socket import *
from constants import *
from StopAndWait import *
from utils import *


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose",
                       required=False, help="increase output verbosity",
                       action="store_true")
    group.add_argument("-q", "--quiet",
                       required=False, help="decrease output verbosity",
                       action="store_true")
    parser.add_argument("-H", "--host",
                        dest="ADDR", required=True, help="server IP address",
                        action="store", type=str)
    parser.add_argument("-p", "--port",
                        dest="PORT", required=True, help="server port",
                        action="store", type=int)
    parser.add_argument("-d", "--dst",
                        dest="FILEPATH",
                        required=True, help="destination file path",
                        action="store", type=str)
    parser.add_argument("-n", "--name",
                        dest="FILENAME", required=True, help="file name",
                        action="store", type=str)
    parser.add_argument("-sr", "--sel_repeat", dest="SELECT_REPEAT",
                        required=True, help="protocol", action="store", 
                        type=str2bool)
    return parser.parse_args()


def handshake_download(file_name, reader, client_socket, address, port, sel_repeat, logger):
    # 20 bytes para el filename
    file_name = file_name.split("/")[-1]
    file_name = "}" * (20 - len(str(file_name))) + str(file_name)
    # Arrancamos los numeros de secuencia con 00000
    initial_seqn = "0" * SEQN_LENGTH
    header = f"{initial_seqn}{START}{DOWNLOAD}{file_name}{sel_repeat}"
    end_time = time.time()

    while True:
        try:
            client_socket.sendto(header.encode(), (address, port))
            client_socket.settimeout(TIMEOUT_SECONDS)

            msj, server_data = client_socket.recvfrom(HANDSHAKE_SIZE)
        except timeout:
            logger.error("Server not available now, try again later.")
            return False, None
        except:
            return False, None

        decoded_buffer = msj.decode()

        if decoded_buffer == INVALID_OP:
            logger.error("Operation you suggested is invalid")
            try:
                reader.close_file()
                client_socket.close()
            except:
                pass
            return False, None

        if decoded_buffer == str(ACK):
            return True, server_data

        current_time = time.time()

        if current_time - end_time >= 3:
            break


def download(args):
    logger = get_logger(args.verbose, args.quiet)
    print("Press q to quit: ")
    client_socket = socket(AF_INET, SOCK_DGRAM)

    file_name = f"{args.FILEPATH}/{args.FILENAME}"
    logger.warning("Client ready to download a file")

    reader = FileReader(file_name)

    result, server_info = handshake_download(
        args.FILENAME, reader, client_socket, args.ADDR, args.PORT, check_protocol(args.SELECT_REPEAT), logger
    )

    if result is False:
        return

    if args.SELECT_REPEAT is True:
        # upload_type = Selective_Repeat()
        logger.info("Se usará el protocolo Selective Repeat")
    else:
        download_type = StopAndWait()
        logger.info("Se usará el protocolo Stop&Wait")
    download_type.download_file(client_socket, server_info[0], server_info[1], reader, 0, logger)


def check_protocol(selected_repeat):
    if selected_repeat is True:
        return SELECTIVE_REPEAT
    return STOP_AND_WAIT


download(get_args())