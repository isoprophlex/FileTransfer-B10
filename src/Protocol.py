class Message:
    sqn_number: int
    type: int

    def get_message_type(self):
        return self.type


class Data(Message):
    def __init__(self, number, type, data):
        self.sqn_number = number
        self.type = type
        self.data = data

    def get_data(self):
        return self.data

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(4, byteorder='big')
        type_bytes = self.type.to_bytes(1, byteorder='big')
        return seq_num_bytes + type_bytes + self.data


class Start(Message):
    filename: str
    filesize: int
    operation_type: bool
    protocol_used: bool

    def __init__(self, number, type, filename, filesize, operation_type, protocol):
        self.sqn_number = number
        self.type = type
        self.filename = str(filename.replace("}", ""))
        self.filesize = filesize
        self.operation_type = operation_type
        self.protocol_used = protocol

    def get_filename(self):
        return self.filename

    def get_filesize(self):
        return self.filesize

    def get_operation_type(self):
        return self.operation_type

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(4, byteorder='big')
        type_bytes = self.type.to_bytes(1, byteorder='big')
        operation_bytes = self.operation_type.to_bytes(1)
        filename_bytes = bytes(self.filename, 'utf-8')
        filesize_bytes = self.filesize.to_bytes(4, byteorder='big')

        return seq_num_bytes + type_bytes + operation_bytes + filename_bytes + filesize_bytes


class Error(Message):
    error_type: int

    def __init__(self, number, type, error):
        self.sqn_number = number
        self.type = type
        self.error_type = error

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(4, byteorder='big')
        type_bytes = self.type.to_bytes(1, byteorder='big')
        error_bytes = self.error_type.to_bytes(1, byteorder='big')

        return seq_num_bytes + type_bytes + error_bytes


class ACK(Message):
    ack: bool

    def __init__(self, number, type, value):
        self.sqn_number = number
        self.type = type
        self.ack = value

    def set_ACK(self, value):
        self.ack = value

    def to_bytes(self):
        seq_num_bytes = self.sqn_number.to_bytes(32, byteorder='big')
        type_bytes = self.type.to_bytes(1, byteorder='big')
        ack_bytes = self.ack.to_bytes(1)

        return seq_num_bytes + type_bytes + ack_bytes


class Protocol:
    def message_from_bytes(bytes):
        seq_num = int(bytes[0:4])
        type = int(bytes[4:5])

        if type == 0:
            operation_type = int(bytes[5:6])
            filename = str(bytes[6:26])
            filesize = int(bytes[26:30])
            protocol = int(bytes[30:32])
            return Start(seq_num, type, filename, filesize, operation_type, protocol)

        elif type == 1:
            return Data(seq_num, type, bytes[5:])

        elif type == 2:
            return Error(seq_num, type, int(bytes[5:6]))

        elif type == 3:
            return ACK(seq_num, type, int(bytes[5:6]))

        else:
            raise Exception
