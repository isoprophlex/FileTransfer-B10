import threading
from socket import *
from FileReader import FileReader
# Habría que importar Selective Repeat y Stop and Wait
from utils import *


class ClientManager:
    socket: socket
    client_data: str
    def __init__(self, client_data,  verbose, quiet):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.client_data = client_data
        self.file_reader = None
        self.logger = get_logger(verbose, quiet)

    def connect(self):
        return threading.Thread(target=self.accept_connection)

    def accept_connection(self):
        # Handshake
        if not handshake_response:
            self.logger.error(f"No se pudo establecer la conexión con cliente: {self.client_data}")
            return

        (
            filename,
            filesize,
            operation
        ) = handshake_response

        if operation == DOWNLOAD:


        elif operation == UPLOAD:


        else:
            # Op invalida?