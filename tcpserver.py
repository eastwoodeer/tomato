#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: tcpserver.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 12:27:02>

import time

from ioloop import IOLoop
from iostream import IOStream
from netutil import add_accept_handler, bind_sockets

class TCPServer(object):
    def __init__(self, io_loop=None):
        self._io_loop = io_loop
        self._sockets = {}
            
    def listen(self, port, address=''):
        sockets = bind_sockets(port, address=address)
        self.add_sockets(sockets)

    def add_sockets(self, sockets):
        if self._io_loop is None:
            self._io_loop = IOLoop.current()

        for sock in sockets:
            self._sockets[sock.fileno()] = sock
            add_accept_handler(sock, self._handle_connection,
                               io_loop=self._io_loop)

    def add_socket(self, socket):
        self.add_sockets([socket])

    def handle_stream(self, stream):
        raise NotImplementedError()

    def _handle_connection(self, connection, address):
        print('new connecting......: ', connection, address)
        stream = IOStream(connection, address)
        self.handle_stream(stream)

if __name__ == '__main__':
    server = TCPServer()
    server.listen(9999)
    IOLoop.instance().start()
    
        
