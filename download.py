import argparse
import os
import sys
from socket import socket, AF_INET, SOCK_DGRAM, timeout

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose",
                       required=False, help="increase output verbosity",
                       action="store_true")
    group.add_argument("-q", "--quiet",
                       required=False, help="decrease output verbosity",
                       action="store_true")
    parser.add_argument("-H", "--host",
                        dest="ADDR", required=True, help="server IP address",
                        action="store", type=str)
    parser.add_argument("-p", "--port",
                        dest="PORT", required=True, help="server port",
                        action="store", type=int)
    parser.add_argument("-d", "--dst",
                        dest="FILEPATH",
                        required=True, help="destination file path",
                        action="store", type=str)
    parser.add_argument("-n", "--name",
                        dest="FILENAME", required=True, help="file name",
                        action="store", type=str)
    return parser.parse_args()

