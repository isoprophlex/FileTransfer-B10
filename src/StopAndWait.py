from socket import *

from constants import *
from FileReader import *


# Envío de datos desde el emisor:

# El emisor tiene datos que desea enviar al receptor.
# El emisor coloca los datos en un paquete y lo envía al receptor a través del canal de comunicación (que puede ser una red cableada o inalámbrica).

# Espera del ACK en el emisor:
#
# Después de enviar un paquete, el emisor entra en un estado de espera.
# Espera una confirmación (ACK) del receptor que indica que los datos se han recibido correctamente.

class StopAndWait():
    def upload_file(self, socket, host, port, reader, logger):
        amount_timeouts = 0
        actual_sqn = 0
        try:
            while True:
                sqn_to_send = "0" * (SEQN_LENGTH - len(str(actual_sqn))) + str(actual_sqn)
                data_chunk = sqn_to_send.encode()
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
                    logger.error(f"Timeout number: {amount_timeouts} occurred")
                    if amount_timeouts == MAX_TIMEOUTS:
                        logger.error(
                            f"Maximum amount of timeouts reached: ({MAX_TIMEOUTS}). Closing connection.")
                        break
                else:
                    amount_timeouts = 0

        except:
            logger.error("Error durante la transmisión")
            return

        finally:
            socket.close()

    def send_packet(self, socket, host, port, data, logger):
        try:
            socket.sendto(data, (host, port))
            logger.info(f"Sending {len(data)} bytes.")
        except Exception as e:
            logger.error(f"Error sending packet: {data[0:4]}")

    def wait_for_ack(self, socket, logger):
        try:
            socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el ACK (5 segundos)
            ack = socket.recv(ACK_SIZE)
            logger.info(f"Recibido ACK: {ack[0:4].decode()}")
            return True
        except socket.timeout:
            return False

    def download_file(self, socket, host, port, writer, seq_n, logger):
        amount_timeouts = 0
        try:
            while True:
                data_chunk = self.receive_packet(socket, logger)
                if len(data_chunk) == 5 and data_chunk.decode().endswith("6"):
                    sqn_to_send = "0" * (SEQN_LENGTH - len(str(seq_n))) + str(seq_n)
                    self.send_ack(socket, host, port, sqn_to_send, logger, False)
                    break
                if data_chunk is None:
                    amount_timeouts += 1
                    logger.error(f"Timeout number {amount_timeouts}!")
                    if amount_timeouts >= MAX_TIMEOUTS:
                        logger.error(f"Maximum amount of timeouts reached: ({MAX_TIMEOUTS}). Closing connection.")
                        break
                else:
                    amount_timeouts = 0
                    writer.write_file(data_chunk[SEQN_LENGTH:])
                    sqn_to_send = "0" * (SEQN_LENGTH - len(str(seq_n))) + str(seq_n)
                    self.send_ack(socket, host, port, sqn_to_send, logger, True)
                    seq_n += 1

        except:
            logger.error("Error durante la descarga")

        finally:
            logger.info("Upload done succesfully!")
            socket.close()

    def receive_packet(self, socket, logger):
        try:
            socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el paquete (5 segundos)
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