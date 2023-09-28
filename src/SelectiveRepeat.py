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

    def print(self):
        return (f"status : {self.status} and data is not null: {self.data_is_not_null()}")



class SelectiveRepeat():
    def __init__(self):
        self.TIMEOUT_SECONDS = 3
        self.MAX_TIMEOUTS = 10
        self.window_size = 4  # Adjust the window size
        self.base = 0
        self.next_sqn = 0
        self.total_packets = 10
        self.packets = [SRPacket() for _ in range(self.total_packets)]
        self.last_sqn_writed = -1 
        self.alive = True

    def upload_file(self, socket, host, port, reader, logger):
        logger.info("start upload_file")
        amount_timeouts = 0
        bytes_read = ""
        try:
            while self.alive:
                while self.next_sqn_in_window(logger) and not reader.is_closed():
                    sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
                    data_chunk = sqn_to_send.encode()
                    bytes_read = (reader.read_file(STD_PACKET_SIZE))

                    if not bytes_read or bytes_read == b'':
                        reader.close_file()
                        end_chunk = f"{sqn_to_send}{ACK_FIN}"
                        self.packets[self.next_sqn].set_data(end_chunk.encode())
                        self.alive = False
                        break  # Fin del archivo
                    
                    data_chunk += bytes_read
                    self.packets[self.next_sqn].set_data(data_chunk)
                    self.next_sqn += 1
                    #self.print_packets(logger)
                
                self.try_send_window(socket, host, port, logger)
                
                # Esperar el ACK del servidor
                self.try_receive_ack(socket, logger)
                
        except Exception as e:
            logger.error(f"Error durante la transmisión: {e}")
            return

        finally:
            socket.close()
        
        logger.info("end upload_file")

    def download_file(self, socket, host, port, writer, seq_n, logger):
        try:
            while self.alive:
                self.try_receive_window(socket, host, port, logger)

                for i in range(self.window_size):
                    if i == self.last_sqn_writed + 1 and self.packets[i].data_is_not_null():
                        writer.write_file(self.packets[i].get_data())
                        self.last_sqn_writed +=1
                
        except Exception as e:
            logger.error(f"Error durante la descarga - {e}")

        finally:
            logger.info("Upload done succesfully!")
            socket.close()

    # Additional methods specific to Selective Repeat protocol
    def try_send_window(self, socket, host, port, logger):
        logger.info("start try_send_window")
        if self.base + self.window_size < self.total_packets:
            for i in range(self.base, self.base + self.window_size):
                #self.print_packets(logger)
                if self.packets[i].is_not_send() and self.packets[i].data_is_not_null():
                    try:
                        socket.sendto(self.packets[i].get_data(), (host, port))
                        logger.info(f"Sending {len(self.packets[i].get_data())} bytes.")
                        self.packets[i].set_wait_ack()
                    except Exception as e:
                        logger.error(f"Error sending packet: {self.packets[i].get_data()[0:4]}")
        else :            
            for i in range(self.base, self.window_size - 1):
                if self.packets[i].is_not_send() and self.packets[i].data_is_not_null():
                    try:
                        socket.sendto(self.packets[i].get_data(), (host, port))
                        logger.info(f"Sending {len(self.packets[i].get_data())} bytes.")
                        self.packets[i].set_wait_ack()
                    except Exception as e:
                        logger.error(f"Error sending packet: {self.packets[i].get_data()[0:4]}")

        logger.info("end try_send_window")
       

    def try_receive_window(self, socket, host, port, logger):
        for i in range(self.window_size):
            try:
                socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el paquete (5 segundos)
                data_chunk = socket.recv(STD_PACKET_SIZE + 5)
                logger.info(f"Packet of {len(data_chunk)} bytes received.")
                
                self.next_sqn = int(data_chunk[0:4].decode())
                logger.info(f"Packet {self.next_sqn} received.")

                if self.next_sqn_in_window(logger):
                    if len(data_chunk) == 5 and data_chunk.decode().endswith(str(ACK_FIN)):
                        sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
                        self.send_ack(socket, host, port, sqn_to_send, logger, True)
                        self.alive = False
                        break
                    #if data_chunk is None:
                    #    amount_timeouts += 1
                    #    logger.error(f"Timeout number {amount_timeouts}!")
                    #    if amount_timeouts >= MAX_TIMEOUTS:
                    #        logger.error(f"Maximum amount of timeouts reached: ({MAX_TIMEOUTS}). Closing connection.")
                    #        break
                    else:
                        #amount_timeouts = 0
                        sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
                        self.send_ack(socket, host, port, sqn_to_send, logger, False)

                    self.packets[self.next_sqn].set_data(data_chunk[SEQN_LENGTH:])
                    self.packets[self.next_sqn].set_already_ack()

                    if self.next_sqn == self.base:
                        self.base +=1
                        

            #except socket.timeout:
            #    logger.error("Error receiving packet - timeout")
            except Exception as e:
                logger.error(f"Error receiving packet {e}")

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

    def try_receive_ack(self, socket, logger):
        logger.info("start try_receive_ack")
        while True:
            try:
                socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el ACK (5 segundos)
                ack = socket.recv(ACK_SIZE)
                seq_num = int(ack[0:4].decode())
                logger.info(f"Recibido ACK: {seq_num}")
                self.packets[seq_num].set_already_ack()
                if seq_num == self.base:
                    self.base +=1
                    if self.base == self.total_packets:
                        self.base = 0
            #except socket.timeout:
            except Exception as e:
                logger.error(f"error in try_receive_ack base: {self.base} - error : {e}")
                break
        
        logger.info("end try_receive_ack")

    def next_sqn_in_window(self, logger):
        sum = self.base + self.window_size
        if sum < self.total_packets:
            if self.next_sqn < sum:
                logger.info(f"next_sqn_in_window return true for next_sqn : {self.next_sqn}")
                return True
        else:
            if self.next_sqn < self.base and self.next_sqn < sum - self.total_packets:
                logger.info(f"next_sqn_in_window return true for next_sqn : {self.next_sqn}")
                return True
            elif self.next_sqn >= self.base and self.next_sqn < self.total_packets:
                logger.info(f"next_sqn_in_window return true for next_sqn : {self.next_sqn}")
                return True

        logger.info(f"next_sqn_in_window return FALSE for next_sqn : {self.next_sqn}")
        return False

    def print_packets(self, logger):
        for x in range(0, self.total_packets):
            logger.info(f"packet {x} : {self.packets[x].print()}")
