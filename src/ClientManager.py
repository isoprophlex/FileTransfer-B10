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
        self.protocol = Protocol()

    def connect(self):
        return threading.Thread(target=self.accept_connection)

    def accept_connection(self):
        handshake_result = self.handshake()
        if not handshake_result:
            self.logger.error(f"Handshake with: {self.client_data} client failed")
            return
        (
            operation_type,
            filename,
            filesize,
            operation,
            client_name,
            sqn_number,
            client_port,
            protocol
        ) = handshake_result

        if operation == DOWNLOAD:
                    #DOWNLOAD


        elif operation == UPLOAD:
                    #UPLOAD

        else:
            socket.sendto(str(ErrorMsg.OPERATION_NOT_FOUND).encode(), (client_name, client_port))
            self.logger.error("The opeartion suggested is invalid.")

    def handshake(self):
        client_message = self.data_received
        start_message = Protocol.message_from_bytes(client_message)
        if start_message.get_message_type() != START_MESSAGE:
            self.logger.error("Error: Wrong type of message.")
            return False
        filename = start_message.get_filename()
        filesize = start_message.get_filesize()
        try:
            if not start_message.get_operation_type():  # the client asks for an upload
                if int(filesize) > MAX_FILE_SIZE:
                    socket.sendto(MAX_FILE_REACHED.encode(), self.client_address)
                    self.logger.error("El tamaño del archivo es demasiado grande")
                    return False

            socket.sendto(ACK_SYN.encode(), (self.client_address[0], int(self.client_address[1])))
            return start_message.get_operation_type(), filename, filesize, start_message.sqn_number, self.client_address[
                0], self.client_address[1], start_message.protocol_used
        except Exception as e:
            self.logger.error(f"Handshake invalido para {client_message}: {e}")
            return False