import argparse, traceback
import sys, threading, os
from socket import socket, AF_INET, SOCK_DGRAM, timeout, SHUT_RD
from lib.exceptions import *
from lib.constants import *
from lib.logger import *
from lib.verify_checksum import *
from Protocol import *
from download import *

class InvalidOperationType(Exception):
    pass

def get_args():
    verbose = args.VERBOSE
    quiet = args.QUIET
    ip = args.ADDR
    port = int(args.PORT)
    validate_port(port)
    path = args.PATH
    validate_directory(path)
    return verbose, quiet, ip, port, path

def start_upload(file_dir, file_name):
    logger.debug(f"Cargando {file_name} en {file_dir}")


def new_connection(directory : str, message : Start):
    file_dir = os.path.join(directory, message.filename)
    if message.operation_type == UPLOAD:
        start_upload(file_dir, message.filesize)
    if message.operation_type == DOWNLOAD:
        with open(file_dir, 'wb+') as file:
            try:
                logger.debug(f"Iniciando descarga de {file_dir}")
            except timeout:
                pass

    else:
        raise InvalidOperationType("Operacion invalida.")


class Listener:
    def __init__(self, sock: socket, directory):
        self.sock = sock
        self.directory = directory
        self.clients = {}
        self.running = False
        self.thread = threading.Thread(target=self._run)
    
    def start(self):
        self.thread.start()

    def _run(self):
        self.running = True
        #Este loop procesa las nuevas conexiones
        while self.running:
            try:
                data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
                check, data_recv = verify_checksum(data)
                if not check:
                    continue
                
                message = Message.read(data_recv)
                if message.type == Start.type:
                    logger.debug("Nueva conexion.")
                    client = threading.Thread(target=new_connection, args=(message))
            except timeout:
                pass
            except OSError as e:
                if self.running:
                    raise e
                else:
                    logger.debug("El servidor no acepta mas clientes.")


def main():
    try:
        verbose, quiet, ip, port, directory = get_args()
    except InvalidPort:
        sys.exit(1)
    except DirectoryNotFound:
        sys.exit(1)
    
    
    logger.info(f"Iniciando servidor en {ip}:{port}")
    logger.info(f"Almacenamiento del servidor en {directory}")
    skt = socket(AF_INET, SOCK_DGRAM)
    try:
        skt.bind((ip,port))
    except OSError as e:
        logger.error(f"Error, no se pudo conectar a la direccion indicada: {e.strerror}")
        sys.exit(1)
    skt.settimeout(TIMEOUT)

    #INICIAR MANEJADOR DE CLIENTES
    #  . . .

    try:
        key = ''
        while key != 'q':
            key = input('Introduzca q para finalizar con la ejecucion del '
                    'servidor\n')
    except KeyboardInterrupt:
        logger.info("Interrupcion de teclado detectada.")
        #Cerrar hilos clientes
    
    skt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", dest="VERBOSE", required=False,
                       help="increase output verbosity",
                       action="store_true")
    group.add_argument("-q", "--quiet", dest="QUIET", required=False,
                       help="decrease output verbosity",
                       action="store_true")
    parser.add_argument("-H", "--host", dest="ADDR", required=True,
                        help="service IP address", action="store", type=str)
    parser.add_argument("-p", "--port", dest="PORT", required=True,
                        help="service port", action="store", type=int)
    parser.add_argument("-s", "--storage", dest="PATH", required=True,
                        help="storage dir path", action="store", type=str)
    args = parser.parse_args()
    try:
        main()
        logger.info("Cerrando servidor...")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        logger.error(e)
        sys.exit(1)