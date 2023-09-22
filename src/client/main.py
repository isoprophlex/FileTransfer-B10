from socket import *
import sys

def main():
    try:
        if len(sys.argv) != 1:
            print("Bad program call.")
            return -1

        # print(f"arg 0 {sys.argv[0]}")
        # client.run()
        print("client main")
        serverName = '127.0.0.1'
        serverPort = 12000
        serverAddress = (serverName, serverPort)
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        
        while True:
            message = input("Input lowercase sentence (or 'q' to quit): ")
            if message.strip().lower() == 'q':
                break
            clientSocket.sendto(message.encode(), serverAddress)
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
            print("serverAddress: ", serverAddress)
            print(modifiedMessage.decode())

            
        clientSocket.close()

        return 0

    except Exception as err:
        print(f"Something went wrong and an exception was caught: {str(err)}")
        return -1

if __name__ == '__main__':
    sys.exit(main())
