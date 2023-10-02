from socket import socket, timeout
from constants import *
from FileReader import *
import time

NOT_SEND = 0
WAIT_ACK = 1
ALREADY_ACK = 2

class SRPacket():
    def __init__(self, timeout, count):
        self.status = NOT_SEND
        self.data = ""
        self.start_time = None
        self.TIMEOUT_SECONDS = timeout
        self.MAX_TIMEOUTS = count
        self.timeout_count = 0

    def is_already_ack(self):
        return self.status == ALREADY_ACK

    def is_wait_ack(self):
        return self.status == WAIT_ACK

    def is_not_send(self):
        return self.status == NOT_SEND

    def set_already_ack(self):
        self.status = ALREADY_ACK
        self.start_time = None

    def set_wait_ack(self):
        self.status = WAIT_ACK
        self.start_time = time.time()

    def set_not_send(self):
        self.status = NOT_SEND
        self.start_time = None

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def data_is_not_null(self):
        return self.data != ""

    def has_timed_out(self):
        if self.start_time is not None:
            ret = time.time() - self.start_time > self.TIMEOUT_SECONDS
            if ret:
                self.timeout_count +=1
                if self.timeout_count == self.MAX_TIMEOUTS:
                    raise Exception("MAX TIMEOUTS REACHED")
            return ret
        return False

    def print(self):
        return f"status : {self.status} and data is not null: {self.data_is_not_null()}"


class SelectiveRepeat():
    def __init__(self):
        self.TIMEOUT_SECONDS = 0.03
        self.MAX_TIMEOUTS = 10
        self.last_packet_time = time.time()
        self.window_size = 20  # Adjust the window size
        self.base = 0
        self.next_sqn = 0
        self.total_packets = 50
        self.packets = [SRPacket(self.TIMEOUT_SECONDS, self.MAX_TIMEOUTS) for _ in range(self.total_packets)]
        self.last_sqn_writed = -1 
        self.alive = True
        self.exception_exit = False

    def upload_file(self, socket, host, port, reader, logger):
        start_time = time.time()
        bytes_read = ""
        bytes_count = 0
        size = reader.get_file_size()
        try:
            while not self.should_stop():
                        
                while self.next_sqn_in_window(logger) and self.alive:
                    sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
                    data_chunk = sqn_to_send.encode()
                    bytes_read = reader.read_file(STD_PACKET_SIZE)
                    bytes_count += len(bytes_read)

                    if not bytes_read or bytes_read == b'':
                        self.alive = False
                        continue
                    data_chunk += bytes_read
                    self.packets[self.next_sqn].set_data(data_chunk)
                    self.packets[self.next_sqn].set_not_send()
                    self.next_sqn += 1
                    if self.next_sqn == self.total_packets:
                        self.next_sqn = 0
                self.try_send_window(socket, host, port, logger)
                # Esperar el ACK del servidor
                self.try_receive_ack(socket, logger)
                self.evaluate_packet_timeouts(socket, host, port, logger)
            self.end(socket, host, port, logger)
        except Exception as e:
            logger.error(f"Error during transmission: {e}")
            self.exception_exit = True
        finally:
            socket.close()
            logger.error(f"{time.time() - start_time}")
        return self.exception_exit

    def download_file(self, socket, host, port, writer, seq_n, logger):
        try:
            while self.alive:
                self.try_receive_window(socket, host, port, logger)
                for i in range(self.base, self.base + self.window_size):
                    i = i % self.total_packets
                    logger.info(f"iteration {i}")
                    if i == self.last_sqn_writed + 1 and self.packets[i].data_is_not_null():
                        logger.info(f"writting {i}")
                        writer.write_file(self.packets[i].get_data())
                        self.last_sqn_writed +=1
                        if self.last_sqn_writed == self.total_packets-1:
                            self.last_sqn_writed = -1
                    else:
                        break
                self.update_recieve_based()
                logger.info(f"new base : {self.base}")
            logger.info("Download done")
        except Exception as e:
            self.exception_exit = True
            logger.error(f"Error during download: {e}")
        finally:
            socket.close()
        return self.exception_exit

    # Additional methods specific to Selective Repeat protocol
    def try_send_window(self, socket, host, port, logger):
        for i in range(self.base, self.base + self.window_size):
            i %= self.total_packets
            if self.packets[i].is_not_send() and self.packets[i].data_is_not_null():
                try:
                    socket.sendto(self.packets[i].get_data(), (host, port))
                    logger.info(f"Sending {len(self.packets[i].get_data())} bytes.")
                    self.packets[i].set_wait_ack()
                except Exception as e:
                    logger.error(f"Error sending packet: {self.packets[i].get_data()[0:4]} - {e}")

    def try_receive_window(self, socket, host, port, logger):
        try:
            for _ in range(self.window_size):
                socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el paquete (5 segundos)
                data_chunk = socket.recv(STD_PACKET_SIZE + 5)
                self.last_packet_time = time.time()
                self.next_sqn = int(data_chunk[0:4].decode())
                if self.next_sqn_in_window(logger):
                    if len(data_chunk) == 5 and data_chunk.decode().endswith(str(ACK_FIN)):
                        sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
                        self.send_ack(socket, host, port, sqn_to_send, logger, True)
                        self.alive = False
                        break
                    else:
                        sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
                        self.send_ack(socket, host, port, sqn_to_send, logger, False)

                    self.packets[self.next_sqn].set_data(data_chunk[SEQN_LENGTH:])
                    self.packets[self.next_sqn].set_already_ack()

                    
        except timeout:
            logger.info("Error receiving packet - timeout")
            current_time = time.time()
            if current_time - self.last_packet_time > MAX_TIME_WITHOUT_PACK:
                raise Exception("Timeout expired, no packets received.")
        except Exception as e:
            logger.error(f"Error receiving packet : {e}")

    def send_ack(self, socket, host, port, seq_n, logger, is_FIN):
        if not is_FIN:
            try:
                ack_message = f"{seq_n}{ACK}"
                socket.sendto(ack_message.encode(), (host, port))
                logger.info(f"Sending ACK: {seq_n}")
            except:
                logger.error(f"Error sending ACK - {e}")
        else:
            try:
                ack_message = f"{seq_n}{ACK_FIN}"
                socket.sendto(ack_message.encode(), (host, port))
                logger.info(f"Sending ACK FIN: {seq_n}")
            except:
                logger.error(f"Error sending ACK - {e}")


    def try_receive_ack(self, socket, logger):
        logger.info("start try_receive_ack")
        it = 0
        while True:
            try:
                it += 1
                socket.settimeout(TIMEOUT_SECONDS)  # Establecer un tiempo de espera para el ACK (5 segundos)
                ack = socket.recv(ACK_SIZE)
                seq_num = int(ack[0:4].decode())
                logger.info(f"Recibido ACK: {seq_num}")
                self.packets[seq_num].set_already_ack()
                if seq_num == self.base:
                    self.packets[self.base] = SRPacket(self.TIMEOUT_SECONDS, self.MAX_TIMEOUTS) 
                    self.base +=1
                    if self.base == self.total_packets:
                        self.base = 0
                    for _ in range(self.window_size-it):
                        if self.packets[self.base].is_already_ack():
                            self.packets[self.base] = SRPacket(self.TIMEOUT_SECONDS, self.MAX_TIMEOUTS) 
                            self.base += 1
                            if self.base == self.total_packets:
                                self.base = 0
                        else: 
                            break
            except timeout:
                logger.info("not more ACK in window")
                break
            except Exception as e:
                logger.error(f"error in try_receive_ack base: {self.base} - error : {e}")
                raise e

        logger.info("end try_receive_ack")

    def next_sqn_in_window(self, logger):
        end = (self.base + self.window_size) % self.total_packets

        if end > self.base and self.base <= self.next_sqn < end:
            return True
        elif end < self.base and (0 <= self.next_sqn < end or self.base <= self.next_sqn < self.total_packets):
            return True

        logger.info(f"next_sqn_in_window return FALSE for next_sqn : {self.next_sqn} - base : {self.base}")
        return False


    def evaluate_packet_timeouts(self, socket, host, port, logger):
        try:
            for i in range(self.base, self.base + self.window_size):
                i %= self.total_packets  # Wrap around if index exceeds total_packets
                if self.packets[i].is_wait_ack() and self.packets[i].has_timed_out():
                    logger.info(f"Packet {i} timed out. Resending...")
                    socket.sendto(self.packets[i].get_data(), (host, port))
                    self.packets[i].set_wait_ack()
        except Exception as e:
            if str(e) == "MAX TIMEOUTS REACHED":
                raise e
            logger.error(f"Error in evaluate_packet_timeouts: {e}")

        logger.info("end evaluate_packet_timeouts")
        
    def update_recieve_based(self): 
        while True:
            if self.packets[self.base].is_already_ack():
                self.packets[self.base] = SRPacket(self.TIMEOUT_SECONDS, self.MAX_TIMEOUTS) 
                self.base += 1
                if self.base == self.total_packets:
                    self.base = 0
            else: 
                break

    def should_stop(self):
        if not self.alive:
            for i in range(self.base, self.base + self.window_size):
                i %= self.total_packets  # Wrap around if index exceeds total_packets
                if self.packets[i].is_wait_ack():
                    return False
            
            return True

        return False

    def end(self, socket, host, port, logger):
        sqn_to_send = "0" * (SEQN_LENGTH - len(str(self.next_sqn))) + str(self.next_sqn)
        end_chunk = f"{sqn_to_send}{ACK_FIN}"
        self.packets[self.next_sqn].set_data(end_chunk.encode())
        self.packets[self.next_sqn].set_not_send()
        self.try_send_window(socket, host, port, logger)
        while not self.should_stop():
            # Esperar el ACK del servidor
            self.try_receive_ack(socket, logger)

            self.evaluate_packet_timeouts(socket, host, port, logger)
        

    def print_packets(self, logger):
        for x in range(0, self.total_packets):
            logger.info(f"packet {x} : {self.packets[x].print()}")
