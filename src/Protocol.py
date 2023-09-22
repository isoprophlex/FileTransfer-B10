class Message:
    sqn_number: int
    type: int


class Data (Message):
    def __init__(self, number, type, data):
        self.sqn_number = number
        self.type = type
        self.data = data

    def get_data(self):
        return self.data

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(32, byteorder='big')
        type_bytes = self.type.to_bytes(4, byteorder='big')
        return seq_num_bytes + type_bytes + self.data

class Start (Message):
    filename: str
    filesize: int
    operation_type: bool
    def __init__(self, number, type, filename, filesize, operation_type):
        self.sqn_number = number
        self.type = type
        self.filename = filename
        self.filesize = filesize
        self.operation_type = operation_type

    def get_filename(self):
        return self.filename
    def get_filesize(self):
        return self.filesize
    def get_operation_type(self):
        return self.operation_type

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(32, byteorder='big')
        type_bytes = self.type.to_bytes(4, byteorder='big')
        operation_bytes = self.operation_type.to_bytes(1)
        filename_bytes = bytes(self.filename, 'utf-8')
        filesize_bytes = self.filesize.to_bytes(32, byteorder='big')

        return seq_num_bytes + type_bytes + operation_bytes + filename_bytes + filesize_bytes



class Error(Message):
    error_type: int
    def __init__(self, number, type, error):
        self.sqn_number = number
        self.type = type
        self.error_type = error

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(32, byteorder='big')
        type_bytes = self.type.to_bytes(4, byteorder='big')
        error_bytes = self.error_type.to_bytes(3, byteorder='big')

        return seq_num_bytes + type_bytes + error_bytes

    

class ACK(Message):
    ack: bool
    def __init__(self,number, type, value):
        self.sqn_number = number
        self.type = type
        self.ack = value
    def set_ACK(self, value):
        self.ack = value

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(32, byteorder='big')
        type_bytes = self.type.to_bytes(4, byteorder='big')
        ack_bytes = self.ack.to_bytes(1)

        return seq_num_bytes + type_bytes + ack_bytes


class Protocol:
    def message_from_bytes(bytes):
        seq_num = int(bytes[0:32])
        type = int(bytes[32:36])

        match type:
            case 0:
                return
            case 1:
                return
            case 2: 
                return
            case 3:
                return
            case 4:
                return
            case default:
                return
        # La idea es, recibir del socket y ver, si es tal tipo, hago un switch y pruebo ese tipo