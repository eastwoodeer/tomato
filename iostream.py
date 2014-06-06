#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: iostream.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 12:26:45>

import collections

class BaseIOStream(object):
    def __init__(self, io_loop=None, max_buffer_size=None,
                 read_chunk_size=4096):
        self._io_loop = io_loop
        self._max_buffer_size = max_buffer_size or 100*1024*1024
        self._read_chunk_size = read_chunk_size
        self._read_buffer = collections.deque()
        self._write_buffer = collections.deque()

    def fileno(self):
        raise NotImplementedError()

    def read_from_fd(self):
       raise NotImplementedError()

class IOStream(BaseIOStream):
    def __init__(self, socket, *args, **kwargs):
        self._socket = socket
        self._socket.setblocking(False)
        super(IOStream, self).__init__(*args, **kwargs)

    def fileno(self):
        return self._socket.fileno()
