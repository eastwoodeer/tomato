#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: iostream.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 17:16:55>

import collections
import errno
import socket

_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)

class BaseIOStream(object):
    def __init__(self, io_loop=None, max_buffer_size=None,
                 read_chunk_size=4096):
        self._io_loop = io_loop
        self._max_buffer_size = max_buffer_size or 100*1024*1024
        self._read_chunk_size = read_chunk_size
        self._read_buffer = collections.deque()
        self._write_buffer = collections.deque()
        self._closed = False

    def fileno(self):
        raise NotImplementedError()

    def read_from_fd(self):
        raise NotImplementedError()

    def closed(self):
        return self._closed

    def close_fd(self):
        raise NotImplementedError()

    def close(self):
        if not self.closed():
            self.close_fd()
            self._closed = True
   

class IOStream(BaseIOStream):
    def __init__(self, socket, *args, **kwargs):
        self._socket = socket
        self._socket.setblocking(False)
        super(IOStream, self).__init__(*args, **kwargs)

    def fileno(self):
        return self._socket.fileno()

    def close_fd(self):
        self._socket.close()
        self._socket = None

    def read_from_fd(self):
        try:
            chunk = self._socket.recv(self._read_chunk_size)
        except socket.error as e:
            if e.args[0] in _ERRNO_WOULDBLOCK:
                return None
            else:
                raise
        if not chunk:
            self.close()
            return None
        return chunk
