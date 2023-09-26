BUFFER_SIZE = 17000
MAX_FILE_SIZE = 1000000000 # 100 MB
START_MESSAGE = 0
DOWNLOAD = 0
UPLOAD = 1
MAX_FILE_REACHED = "File surpasses size limits"
ACK_SYN = 1


#Protocol
SELECTIVE_REPEAT = 1
STOP_AND_WAIT = 0

# Cuanto tiempo en segundos usamos de timeout
TIMEOUT = 2

MAX_PACKET_SIZE = ((64*1024)+1) #64kB