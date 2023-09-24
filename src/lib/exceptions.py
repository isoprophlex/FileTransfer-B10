class InvalidPort(Exception):
    def __init__(self):
        #TODO: CAMBIAR AL LOGGER.ERROR
        print('ERROR - Puerto Invalido: debe ingresar un puerto que:\
              \n1) Sea mayor a 1024 \
              \n2) Sea distinto al 8080 y 8443\
              \n3) Sea menor a 65535 valor maximo de un puerto')

class DirectoryNotFound(Exception):
    def __init__(self):
        #TODO: CAMBIAR AL LOGGER.ERROR
        print('ERROR - El directorio ingresado para \
                     almacenar los archivos no existe')


def validate_port(port):
    used_ports = list(range(0, 1024))
    used_ports.append(8080)
    used_ports.append(8443)
    if port in used_ports or port > 65535 or port < 0:
        raise InvalidPort()


def validate_directory(directory):
    if not os.path.exists(directory):
        raise DirectoryNotFound()