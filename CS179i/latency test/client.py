#!/usr/bin/env python3

from os import EX_UNAVAILABLE
import socket
import time
import sys

HOST = '10.0.0.2'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
enable = 1 

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    f = open('dummy','rb')
    for x in f:
        timestart = time.time()
        s.sendall(x)
        data = s.recv(1024)
        timeend = time.time()
        rtt = timeend - timestart
        print("Sent {} bytes with RTT: {} seconds" .format(sys.getsizeof(x),rtt))

