from socket import *

from constants import *
from FileReader import *


class StopAndWait():

    def upload_file(self, socket, host, port, reader, logger):

        current_seqn = 1
        timeout_counter = 0

        try:
            readed_bytes = reader.read_file(STD_PACKET_SIZE)
        except:
            logger.error("Error al leer el archivo")
            return "Error"

        while readed_bytes is not None and readed_bytes != b"":

            # Rellenar seqn
            seqn = "0" * (5 - len(str(current_seqn))) + str(current_seqn)

            bytes = f"{seqn} ".encode()

            bytes += readed_bytes

            try:
                socket.sendto(bytes, (host, port))
            except:
                return

            logger.info(f"Seqn {current_seqn} enviado a {host}:{port}")

            try:
                socket.settimeout(TIMEOUT_SECONDS)
            except:
                return

            try:
                buffer = socket.recv(HANDSHAKE_SIZE)
                if buffer.decode()[:3] == "ACK":
                    timeout_counter = 0
            except timeout:

                timeout_counter += 1
                if timeout_counter == MAX_TIMEOUTS_SAW:
                    logger.error(f"Se cerró la conexión con {host}:{port}")
                    return "Error"
                logger.error(f"Timeout en seqn {current_seqn}")
                continue

            except:
                return

            decoded_buffer = buffer.decode()

            while decoded_buffer != "ACK " + str(
                current_seqn
            ) and decoded_buffer != "ACK " + str(MAX_SEQ_NUMBER):
                bytes = f"{seqn} ".encode()
                bytes += readed_bytes

                try:
                    socket.sendto(bytes, (host, port))
                    socket.settimeout(TIMEOUT_SECONDS)
                except:
                    return "Error"

                try:
                    # Aca esperamos ACK
                    buffer = socket.recv(HANDSHAKE_SIZE)
                    if buffer.decode()[:3] == "ACK":
                        timeout_counter = 0
                except timeout:
                    timeout_counter += 1
                    if timeout_counter == MAX_TIMEOUTS_SAW:
                        logger.error(f"Se cerró la conexión con {host}:{port}")
                        return "Error"
                    logger.error(f"Timeout en seqn {current_seqn}")
                    continue
                except:
                    return "Error"

                decoded_buffer = buffer.decode()

            current_seqn += 1

            # Si sobrepasa length maximo
            if len(str(current_seqn)) > SEQN_LENGTH:
                current_seqn = 0

            # Si la respuesta es "OK" entonces se sigue leyendo el archivo:
            readed_bytes = reader.read_file(STD_PACKET_SIZE)
            if readed_bytes is None:
                return "Error"

        logger.info("Cerrando conexión con servidor...")

        try:
            socket.settimeout(TIMEOUT_SECONDS)
        except:
            return "Error"

        while True:
            try:
                socket.sendto("FIN".encode(), (host, port))
                buffer = socket.recv(BUFFER_SIZE)
            except timeout:
                timeout_counter += 1
                if timeout_counter == MAX_TIMEOUTS_SAW:
                    logger.error(f"Se cerró la conexión con {host}:{port}")
                    return "Error"
                logger.error(f"Timeout en seqn {current_seqn}")
                continue
            except:
                return "Error"

            if buffer.decode() == "ACK FIN":
                break

        try:
            reader.close_file()
            socket.close()
        except:
            pass
        logger.info(f"Socket de upload cerrado en conexión con {host}:{port}")
        return "Ok"

    def download_file(
        self, socket, serverName, serverPort, writer: FileReader, seq_n, logger
    ):
        timeout_counter = 0

        try:
            current_seqn = int(seq_n)  # El que recibí último
        except ValueError:
            logger.error("No se pudo convertir seq_n a entero")
            return "Error"

        while True:

            try:
                socket.settimeout(TIMEOUT_SECONDS)
            except:
                return "Error"

            try:
                buffer = socket.recv(BUFFER_SIZE)
                timeout_counter = 0
                logger.info(
                    f"Seqn {current_seqn} recibido de {serverName}:{serverPort}"
                )
                if buffer.decode() == FIN:
                    break
            except UnicodeDecodeError:
                pass
            except timeout:
                timeout_counter += 1
                if timeout_counter == MAX_TIMEOUTS_SAW:
                    logger.error(f"Se cerró la conexión con {serverName}:{serverPort}")
                    return "Error"
                logger.error(f"Timeout en seqn {current_seqn}")
                continue
            except:
                return "Error"

            seqn = buffer[:5].decode()
            data = buffer[6:]  # 6 porque hay un espacio despues del seqn

            try:
                seqn = int(seqn)
            except ValueError:
                logger.error(
                    f"No se pudo convertir seqn a entero en conexión con {serverName}:{serverPort}"
                )
                continue

            if seqn != current_seqn + 1 and current_seqn != MAX_SEQ_NUMBER:
                # Envío el último que tengo
                try:
                    socket.sendto(
                        f"ACK {current_seqn}".encode(), (serverName, serverPort)
                    )
                except:
                    return "Error"

                continue

            current_seqn += 1

            # Si sobrepasa length maximo
            if len(str(current_seqn)) > SEQN_LENGTH:
                current_seqn = 0

            # Si sale OK se envía ACK del que recibí
            try:
                socket.sendto(f"ACK {current_seqn}".encode(), (serverName, serverPort))
            except:
                return "Error"

            written_bytes = writer.write_file(data)
            if written_bytes is None:
                return "Error"

            while written_bytes < len(data):
                written_bytes += writer.write_file(data[written_bytes:])
                if written_bytes is None:
                    return "Error"

        logger.info("Cerrando conexion con servidor...")

        try:
            socket.sendto(ACK_FIN.encode(), (serverName, serverPort))
            writer.close_file()
            socket.close()
        except:
            pass

        logger.info("Socket de download cerrado")
        return "Ok"