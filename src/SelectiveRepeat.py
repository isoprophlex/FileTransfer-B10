from socket import *
from constants import *
from FileReader import *

ALREADY_ACK = 0
WAIT_ACK = 1
NOT_SEND = 2

class SRPacket():
    def __init__(self):
        self.status = NOT_SEND
        self.data = ""

    def is_already_ack(self):
        return self.status == ALREADY_ACK

    def is_wait_ack(self):
        return self.status == WAIT_ACK

    def is_not_send(self):
        return self.status == NOT_SEND

    def set_already_ack(self):
        self.status = ALREADY_ACK

    def set_wait_ack(self):
        self.status = WAIT_ACK

    def set_not_send(self):
        self.status = NOT_SEND

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def data_is_not_null(self):
        return self.data != ""



class SelectiveRepeat():
    def __init__(self):
        self.TIMEOUT_SECONDS = 3
        self.MAX_TIMEOUTS = 10
        self.window_size = 4  # Adjust the window size
        self.send_base = 0
        self.next_sqn = 0
        self.total_packets = 10
        self.packets = [SRPacket()] * total_packets

    def upload_file(self, socket, host, port, reader, logger):
        amount_timeouts = 0
        bytes_read = ""
        try:
            while True:
                while self.next_sqn_in_window() and not reader.is_closed():
                    sqn_to_send = "0" * (SEQN_LENGTH - len(str(next_sqn))) + str(next_sqn)
                    data_chunk = sqn_to_send.encode()
                    bytes_read = (reader.read_file(STD_PACKET_SIZE))

                    if not bytes_read or bytes_read == b'':
                        reader.close()
                        end_chunk = f"{sqn_to_send}{ACK_FIN}"
                        self.packets[self.next_sqn].set_data(end_chunk.encode())
                        break  # Fin del archivo
                    
                    data_chunk += bytes_read
                    self.packets[self.next_sqn].set_data(data_chunk.encode())
                    self.next_sqn += 1
                
                self.try_send_window(socket, host, port, logger)
                
                # Esperar el ACK del servidor
                self.receive_ack(socket, logger)
                
        except:
            logger.error("Error durante la transmisión")
            return

        finally:
            socket.close()

    def download_file(self, socket, host, port, writer, seq_n, logger):
        # Implementation for receiving packets with Selective Repeat
        pass

    # Additional methods specific to Selective Repeat protocol
    def try_send_window(self, socket, host, port, logger):
        for i in range(self.send_base, self.send_base + self.window_size):
            if self.packets[i].is_not_send() and self.packets[i].is_not_null():
                try:
                    socket.sendto(data, (host, port))
                    logger.info(f"Sending {len(data)} bytes.")
                    self.packets[i].set_wait_ack()
                except Exception as e:
                    logger.error(f"Error sending packet: {data[0:4]}")
       

    def receive_window(self, socket, host, port, logger):
        # Receive a window of packets
        pass

    def send_ack(self, socket, host, port, seq_n, logger, is_FIN):
        # Implementation for sending acknowledgments
        pass

    def receive_ack(self, socket, logger):
        try:
            socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el ACK (5 segundos)
            ack = socket.recv(ACK_SIZE)
            seq_num = ack[0:4].decode()
            logger.info(f"Recibido ACK: {seq_num}")
            self.packets[seq_num].set_already_ack()
            if seq_num == self.send_base:
                self.send_base +=1
                if self.send_base == self.total_packets:
                    self.send_base = 0
        except socket.timeout:
            logger.error(f"timeout ACK - send_base: {self.send_base}")

    def next_sqn_in_window(self):
        sum = self.send_base + self.window_size
        if sum < self.total_packets:
            if self.next_sqn <= sum:
                return True
        else:
            if self.next_sqn < self.send_base and self.next_sqn < sum - self.total_packets:
                return True
            elif self.next_sqn >= self.send_base and self.next_sqn < self.total_packets:
                return True

        return False


