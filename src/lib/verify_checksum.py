import zlib
from typing import Tuple

def generate_checksum(data : bytes):
    checksum = zlib.crc32(data)
    return (checksum.to_bytes(4, 'big')+data)

def verify_checksum(packet : bytes) -> Tuple[bool,bytes]:
    data = packet[4:]
    checksum = zlib.crc32(data).to_bytes(4,'big')
    return (checksum==packet[0:4],data)