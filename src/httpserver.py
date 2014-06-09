#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: httpserver.py
# Author:   Chenbin
# Time-stamp: <2014-06-09 Mon 15:57:26>

from tcpserver import TCPServer
from ioloop import IOLoop

class HTTPServer(TCPServer):
    def __init__(self, request_callback, io_loop=None, **kwargs):
        self._io_loop = io_loop
        self._request_callback = request_callback
        super(HTTPServer, self).__init__(io_loop=self._io_loop, **kwargs)

    def handle_stream(self, stream, address):
        HTTPConnection(stream, address, self._request_callback)
        
class HTTPConnection(object):
    def __init__(self, stream, address, request_callback):
        self._stream = stream
        self._address = address
        self._request_callback = request_callback

        s = self._stream.read_until(b'\r\n', None)
        # if s is None:
        #     IOLoop.current().add_handler(self._stream.fileno(),
        #                                  self.read_handler, IOLoop.READ)
        # else:
        #     print(s)

    def read_handler(self, fd, events):
        s = self._stream.read_from_fd()
        IOLoop.current().remove_handler(fd)
        print('-->', s)

if __name__ == '__main__':
    server = HTTPServer(None)
    server.listen(9999)
    IOLoop.instance().start()
