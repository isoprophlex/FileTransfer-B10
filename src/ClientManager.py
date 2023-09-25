import threading
from socket import *
from FileReader import FileReader
# Habría que importar Selective Repeat y Stop and Wait
from utils import *
from Protocol import Protocol
from constants import *
from StopAndWait import *


class ClientManager:
    socket: socket
    client_data: str

    def __init__(self, client_address, client_data, verbose, quiet, storage):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.client_address = client_address
        self.file_reader = None
        self.logger = get_logger(verbose, quiet)
        self.data_received = client_data
        self.protocol = Protocol()
        self.storage = storage

    def connect(self):
        return threading.Thread(target=self.accept_connection)

    def accept_connection(self):
        handshake_result = self.handshake()
        if not handshake_result:
            self.logger.error(f"Handshake with: {self.client_address} client failed")
            return
        (
            seq_num,
            type_msg,
            operation_type,
            filename,
            filesize,
            protocol,
            client_name,
            client_port,
        ) = handshake_result

        if operation_type == UPLOAD:
            self.logger.info(f"Server preparado para recibir archivos a {client_name}")
            download_type = self.use_protocol(protocol)
            self.download_file(
                download_type, filename, client_name, client_port, seq_num
            )
        else:
            socket.sendto(str(ErrorMsg.OPERATION_NOT_FOUND).encode(), (client_name, client_port))
            self.logger.error("The operation suggested is invalid.")

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
                    self.logger.error("File too big")
                    return False

            self.socket.sendto(str(ACK_SYN).encode(), (self.client_address[0], int(self.client_address[1])))
            return (start_message.sqn_number, start_message.get_message_type(), start_message.get_operation_type(), filename, filesize,
                    start_message.protocol_used, self.client_address[0], self.client_address[1])
        except Exception as e:
            self.logger.error(f"Handshake invalido para {self.client_address}: {e}")
            return False

    def use_protocol(self, protocol):
        selected = StopAndWait()
        if protocol == "True":
            # selected = Selective_Repeat()
            self.logger.info("Se usará el protocolo Selective Repeat")
        else:
            selected = StopAndWait()
            self.logger.info("Se usará el protocolo Stop&Wait")
        return selected

    def download_file(self, protocol, file_name, client_name, client_port, seq_n):
        self.file_reader = FileReader(os.path.join(self.storage, file_name))
        code = protocol.download_file(
            self.socket, client_name, client_port, self.file_reader, seq_n, self.logger
        )
        if code == str(ERROR):
            self.close_file_reader()
            return

    def close_file_reader(self):
        self.file_reader.close_file()
