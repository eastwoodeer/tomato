#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: httpserver.py
# Author:   Chenbin
# Time-stamp: <2014-08-15 Fri 15:53:51>

import time

from httputil import HTTPHeader
from tcpserver import TCPServer
from ioloop import IOLoop

class HTTPRequest(object):
    def __init__(self, method, uri, version='HTTP/1.0', headers=None,
                 body=None, remote_ip=None, protocol=None, host=None,
                 files=None, connection=None):
        self._method = method
        self._uri = uri
        self._version = version
        self._connection = connection
        self._start_time = time.time()
        self._finish_time = None
        self._remote_ip = remote_ip
        self._body = body or ''

    def finish(self):
        self._connection.close()
        self._finish_time = time.time()


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
        self._request = None

        s = self._stream.read_until(b'\r\n\r\n', self._on_header)

    def read_handler(self, data):
        print('we recive data: ')
        print(data.decode('latin1'))
        self._stream.close()

    def _on_header(self, data):
        try:
            data = data.decode('latin1')
            eol = data.find('\r\n')
            start_line = data[:eol]
            try:
                method, uri, version = start_line.split(' ')
                try:
                    headers = HTTPHeader.parse(data[eol:])
                    print('headers: %s' % headers)
                except ValueError as e:
                    print(e)
                    raise
            except Exception as e:
                print(e)
                raise
            if not version.startswith('HTTP/'):
                print('error http version')
        except:
            print('on header exception.')
            raise
        print(method, uri, version, self._address)
        remote_ip = self._address[0]

        self._request = HTTPRequest(
            connection=self, method=method, uri=uri,
            version=version, headers=headers, remote_ip=remote_ip)
        content_length = headers.get('Content-Length')
        if content_length:
            content_length = int(content_length)
            if content_length > self._stream.max_buffer_size():
                print('Content-Length too long')
                raise
            self._stream.read_bytes(content_length, self._on_request_body)

    def _on_request_body(self, data):
        print('request body: %s' % data)
        self._request.body = data
        if self._request_callback:
            self._request_callback(self._request)


if __name__ == '__main__':
    server = HTTPServer(None, io_loop=IOLoop.current())
    server.listen(9999)
    IOLoop.instance().start()
