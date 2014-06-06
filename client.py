#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: client.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 16:05:18>

# Echo client program
import socket
import sys

HOST = '10.74.169.42'
PORT = 9999              # The same port as used by the server

def init_socket():
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError as msg:
            s = None
            continue
        try:
            s.connect(sa)
        except OSError as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print('could not open socket')
        sys.exit(1)
    return s

def send_msg(s, msg):
    s.sendall(msg)
    s.close()

if __name__ == '__main__':
    s = init_socket()
    msg = sys.argv[1]
    send_msg(s, msg.encode('ascii'))
    
