import os
from socket import *
import sys
import threading

def handle_socket_logic():
    try:
        serverPort = 12000
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', serverPort))
        print("The server is ready to receive")

        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            print("Client Address: ", clientAddress)
            modifiedMessage = message.decode().upper()
            serverSocket.sendto(modifiedMessage.encode(), clientAddress)
            print("Message sent")

    except Exception as err:
        print(f"Something went wrong and an exception was caught: {str(err)}")

def main():
    try:
        if len(sys.argv) != 1:
            print("Bad program call.")
            return -1

        print("server main")

        socket_thread = threading.Thread(target=handle_socket_logic)
        socket_thread.daemon = True
        socket_thread.start()

        while True:
            user_input = input("")
            if user_input.strip().lower() == 'q':
                os._exit(0)

        return 0

    except Exception as err:
        print(f"Something went wrong and an exception was caught: {str(err)}")
        return -1

if __name__ == '__main__':
    sys.exit(main())
