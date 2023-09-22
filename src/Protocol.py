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


class Error(Message):
    error_type: int
    def __init__(self, error):
        self.error_type = error

class ACK(Message):
    ack: bool
    def __init__(self, value):
        self.ack = value
    def set_ACK(self, value):
        self.ack = value
class Protocol:
        # La idea es, recibir del socket y ver, si es tal tipo, hago un switch y pruebo ese tipo