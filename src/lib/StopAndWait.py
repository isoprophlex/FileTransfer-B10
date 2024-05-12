from random import randint
import socket
from socket import socket, timeout
import time

from src.lib.constants import *
from src.lib.FileReader import *


class StopAndWait():
    def __init__(self):
        self.TIMEOUT_SECONDS = 5
        self.MAX_TIMEOUTS = 3
        self.exception_exit = False

    def upload_file(self, socket, host, port, reader, logger):
        amount_timeouts = 0
        actual_sqn = 0
        previous_sqn = -1
        bytes_read = ""

        try:
            while True:
                sqn_to_send = "0" * (SEQN_LENGTH - len(str(actual_sqn))) + str(actual_sqn)
                data_chunk = sqn_to_send.encode()
                if actual_sqn == previous_sqn + 1:
                    bytes_read = (reader.read_file(STD_PACKET_SIZE))
                if not bytes_read or bytes_read == b'':
                    end_chunk = f"{sqn_to_send}{ACK_FIN}"
                    self.send_packet(socket, host, port, end_chunk.encode(), logger)
                    ack_received = self.wait_for_ack(socket, logger)
                    break  # Fin del archivo
                data_chunk += bytes_read
                self.send_packet(socket, host, port, data_chunk, logger)
                # Esperar el ACK del servidor
                ack_received = self.wait_for_ack(socket, logger)
                if not ack_received:
                    amount_timeouts += 1
                    logger.info(f"Timeout number: {amount_timeouts} occurred")
                    if amount_timeouts == self.MAX_TIMEOUTS:
                        logger.error(
                            f"Maximum amount of timeouts reached: ({self.MAX_TIMEOUTS}). Closing connection.")
                        self.exception_exit = True
                        break
                    previous_sqn = actual_sqn
                else:
                    amount_timeouts = 0
                    previous_sqn = actual_sqn
                    actual_sqn += 1
                    if actual_sqn == 9999:
                        previous_sqn = -1
                        actual_sqn = 0
        except:
            logger.error("Error during transmission")

        finally:
            logger.error("File uploaded successfully")
            socket.close()
        return self.exception_exit

    def send_packet(self, socket, host, port, data, logger):
        try:
            socket.sendto(data, (host, port))
            logger.info(f"Sending {len(data)} bytes.")
        except Exception as e:
            logger.error(f"Error sending packet: {data[0:4]}")

    def wait_for_ack(self, socket, logger):
        try:
            socket.settimeout(self.TIMEOUT_SECONDS)
            ack = socket.recv(ACK_SIZE)
            logger.info(f"Recibido ACK: {ack[0:4].decode()}")
            return True
        except:
            return False

    def download_file(self, socket, host, port, writer, seq_n, logger):
        amount_timeouts = 0
        previous_chunk = ""
        start_time = time.time()
        while True:
            try:
                data_chunk = self.receive_packet(socket, logger)
            except:
                amount_timeouts += 1
                logger.error(f"Timeout number {amount_timeouts}!")
                if amount_timeouts >= self.MAX_TIMEOUTS:
                    self.exception_exit = True
                    logger.error(f"Maximum amount of timeouts reached: ({MAX_TIMEOUTS}). Closing connection.")
                    break
                continue
            if data_chunk == previous_chunk:  # Me llegó de nuevo el mismo paquete
                sqn_to_send = "0" * (SEQN_LENGTH - len(str(seq_n))) + str(seq_n)
                self.send_ack(socket, host, port, sqn_to_send, logger, False)
                break
            if len(data_chunk) == 5 and data_chunk.decode().endswith("6"):
                sqn_to_send = "0" * (SEQN_LENGTH - len(str(seq_n))) + str(seq_n)
                self.send_ack(socket, host, port, sqn_to_send, logger, True)
                break
            if data_chunk is None:
                amount_timeouts += 1
                logger.error(f"Timeout number {amount_timeouts}!")
                if amount_timeouts >= self.MAX_TIMEOUTS:
                    self.exception_exit = True
                    logger.error(f"Maximum amount of timeouts reached: ({MAX_TIMEOUTS}). Closing connection.")
                    break
            elif data_chunk != previous_chunk:
                amount_timeouts = 0
                sqn_to_send = "0" * (SEQN_LENGTH - len(str(seq_n))) + str(seq_n)
                self.send_ack(socket, host, port, sqn_to_send, logger, False)
                try:
                    writer.write_file(data_chunk[SEQN_LENGTH:])
                except:
                    self.exception_exit = True
                    logger.error("Error writing file")
                    break
                previous_chunk = data_chunk
                seq_n += 1
            if seq_n == 9999:
                seq_n = 0000
        if not self.exception_exit:
            logger.error("File downloaded successfully")
        socket.close()
        logger.info(f"Time: {time.time() - start_time}")
        return self.exception_exit

    def receive_packet(self, socket, logger):
        try:
            socket.settimeout(self.TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el paquete (5 segundos)
            data_chunk = socket.recv(STD_PACKET_SIZE + 5)
            logger.info(f"Packet of {len(data_chunk)} bytes received.")
            return data_chunk
        except socket.timeout:
            return None
        except Exception as e:
            logger.error("Error receiving packet")
            return None

    def send_ack(self, socket, host, port, seq_n, logger, is_FIN):
        if not is_FIN:
            try:
                ack_message = f"{seq_n}{ACK}"
                socket.sendto(ack_message.encode(), (host, port))
                logger.info(f"Sending ACK: {seq_n}")
            except:
                logger.error(f"Error sending ACK")
        else:
            try:
                ack_message = f"{seq_n}{ACK_FIN}"
                socket.sendto(ack_message.encode(), (host, port))
                logger.info(f"Sending ACK FIN: {seq_n}")
            except:
                logger.error(f"Error sending ACK")
