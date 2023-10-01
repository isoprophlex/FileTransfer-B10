import os


class FileReader(object):
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
            self.file = open(self.file_name, "b+r")
        if self.file != "File closed":
            read = self.file.read(size)
            self.current_byte += size
            return read

    def write_file(self, buffer):
        if self.file is None:
            self.file = open(self.file_name, "bw+")
        if self.file != "File closed":
            written = self.file.write(buffer)
            return written

    def get_file_size(self):
        file_stats = os.stat(self.file_name)
        return file_stats.st_size

    def close_file(self, exc_exit):
        if self.file and self.file != "File closed" and not exc_exit:
            aux = self.file
            self.file = "File closed"
            aux.close()
        elif self.file and self.file != "File closed" and exc_exit:
            os.remove(self.file)
            self.file = "File closed"

    def is_closed(self):
        return self.file == "File closed"
