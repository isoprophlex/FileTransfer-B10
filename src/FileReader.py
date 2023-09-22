import os


class FileReader:
    def __init__(self, file):
        self.file = None
        self.current_byte = 0
        self.file_name = file

    def read_file(self, size):
        """
        File is a string containing the path to the file to be read.
        Bytes is an integer containing the number of bytes to be read.
        
        """
        if self.file is None:
            self.file = open(self.file_name, "rb")
        if self.file != "File closed":
            readed = self.file.read(size)
            self.current_byte += size
            return readed

    def write_file(self, buffer):
        if self.file is None:
            self.file = open(self.file_name, "wb")
        if self.file != "File closed":
            written = self.file.write(buffer)
            return written

    def get_file_size(self):
        file_stats = os.stat(self.file_name)
        return file_stats.st_size

    def close_file(self):
        if self.file and self.file != "File closed":
            aux = self.file
            self.file = "File closed"
            aux.close()