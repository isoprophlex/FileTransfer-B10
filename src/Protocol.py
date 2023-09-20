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



class Protocol:
    # La idea es, recibir del socket y ver, si es tal tipo, hago un switch y pruebo ese tipo