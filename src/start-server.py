import argparse, traceback
import sys
from socket import socket, AF_INET, SOCK_DGRAM, timeout, SHUT_RD
from lib.exceptions import *
from lib.constants import *

def get_args():
    verbose = args.VERBOSE
    quiet = args.QUIET
    ip = args.ADDR
    port = int(args.PORT)
    validate_port(port)
    path = args.PATH
    validate_directory(path)
    return verbose, quiet, ip, port, path


def main():
    try:
        verbose, quiet, ip, port, directory = get_args()
    except InvalidPort:
        sys.exit(1)
    except DirectoryNotFound:
        sys.exit(1)
    
    
    #TODO: CAMBIAR AL LOGGER.ERROR
    print(f"Iniciando servidor en {ip}:{port}")
    print(f"Almacenamiento del servidor en {directory}")
    skt = socket(AF_INET, SOCK_DGRAM)
    try:
        skt.bind((ip,port))
    except OSError as e:
        print(f"Error, no se pudo conectar a la direccion indicada: {e.strerror}")
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
        print("Interrupcion de teclado detectada.")
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
        #TODO: CAMBIAR AL LOGGER.INFO
        print("Cerrando servidor...")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(e)
        sys.exit(1)