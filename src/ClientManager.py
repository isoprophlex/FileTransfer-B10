import threading
from socket import *
from FileReader import FileReader
# Habría que importar Selective Repeat y Stop and Wait
from utils import *
from Protocol import Protocol
from constants import *


class ClientManager:
    socket: socket
    client_data: str
    def __init__(self, client_address, client_data,  verbose, quiet):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.client_address = client_address
        self.file_reader = None
        self.logger = get_logger(verbose, quiet)
        self.data_received = client_data

    def connect(self):
        return threading.Thread(target=self.accept_connection)
    def handshake(self):
        client_message = self.data_received

        client_message = client_message.decode() #
        client_name, client_port = self.client_address

        try:
            client_file_data = client_message.split()
            if len(client_file_data) == 5:  # the client asks for an upload
                file_size = client_file_data[-1]
                if int(file_size) > MAX_FILE_SIZE:
                    socket.sendto(MAX_FILE_REACHED.encode(), (client_name, client_port))
                    self.logger.error("El tamaño del archivo es demasiado grande")
                    return False

            operation, file_name, seq_n, gobackn = (
                client_file_data[OPERATION],
                client_file_data[FILE_NAME],
                client_file_data[SEQN],
                client_file_data[GOBACKN],
            )

            socket.sendto(ACK_SYNC.encode(), (client_name, int(client_port)))
            return (operation, file_name, seq_n, client_name, int(client_port), gobackn)
        except Exception as e:
            self.logger.error(f"Handshake invalido para {client_message}: {e}")
            return False
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