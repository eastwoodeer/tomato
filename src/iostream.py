#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: iostream.py
# Author:   Chenbin
# Time-stamp: <2014-08-15 Fri 11:27:00>

import collections
import errno
import socket

import ioloop

_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)

# These errnos indicate that a connection has been abruptly terminated.
# They should be caught and handled less noisily than other errors.
_ERRNO_CONNRESET = (errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE)

class BaseIOStream(object):
    def __init__(self, io_loop=None, max_buffer_size=None,
                 read_chunk_size=4096):
        self._io_loop = io_loop
        self._max_buffer_size = max_buffer_size or 100*1024*1024
        self._read_chunk_size = read_chunk_size
        self._read_buffer = collections.deque()
        self._read_buffer_size = 0
        self._read_bytes = None
        self._write_buffer = collections.deque()
        self._read_callback = None
        self._read_delimiter = None
        self._closed = False
        self._state = None

    def max_buffer_size(self):
        return self._max_buffer_size

    def fileno(self):
        raise NotImplementedError()

    def write_to_fd(self):
        raise NotImplementedError()
    
    def read_from_fd(self):
        raise NotImplementedError()

    def closed(self):
        return self._closed

    def close_fd(self):
        raise NotImplementedError()

    def close(self):
        if not self.closed():
            if self._state is not None:
                self._io_loop.remove_handler(self.fileno())
                self._state = None
            self.close_fd()
            self._closed = True

    def read_until(self, delimiter, callback):
        self._set_read_callback(callback)
        self._read_delimiter = delimiter
        self._try_inline_read()

    def read_bytes(self, num_bytes, callback):
        self._set_read_callback(callback)
        self._read_bytes = num_bytes
        self._try_inline_read()

    def _set_read_callback(self, callback):
        assert not self._read_callback, 'Already reading...'
        self._read_callback = callback        
        
    def _try_inline_read(self):
        if self._read_from_buffer():
            return
        try:
            while not self.closed():
                if self._read_to_buffer() == 0:
                    break
        except Exception:
            print('try_inline_read')
            raise
        if self._read_from_buffer():
            return
        self._maybe_add_error_listener()

    def _maybe_add_error_listener(self):
        if self._state is None:
            if self.closed():
                print('already closed')
            else:
                self._add_io_state(ioloop.IOLoop.READ)

    def _add_io_state(self, state):
        if self.closed():
            return
        if self._state is None:
            self._state = ioloop.IOLoop.ERROR | state
            self._io_loop.add_handler(self.fileno(), self._handle_events,
                                      self._state)
        else:
            self._state = self._state | state
            self._io_loop.update_handler(self.fileno(), self._state)

    def _handle_events(self, fd, events):
        print('handle_events')
        if self.closed():
            print('error: already closed')
            return
        try:
            if events & self._io_loop.READ:
                self._handle_read()
            if self.closed():
                return
        except Exception:
            print('handle events exception...')
            self.close()
            raise

    def _handle_read(self):
        try:
            while not self.closed():
                if self._read_to_buffer() == 0:
                    break
        except Exception:
            print('handle_read exception')
            self.close()
            return
        if self._read_from_buffer():
            return

    def _read_to_buffer(self):
        try:
            chunk = self.read_from_fd()
        except (socket.error, IOError, OSError) as e:
            print('read_to_buffer:', e)
            if e.args[0] in _ERRNO_CONNRESET:
                return
            raise
        if chunk is None:
            return 0
        self._read_buffer.append(chunk)
        self._read_buffer_size += len(chunk)
        if self._read_buffer_size > self._max_buffer_size:
            print('buffer exceed')
            self.close()
            raise IOError('reached maxium read buffer size')
        return len(chunk)

    def _read_from_buffer(self):        
        if self._read_bytes is not None and self._read_buffer_size >= self._read_bytes:
            num_bytes = self._read_bytes
            callback = self._read_callback
            self._read_bytes = None
            self._read_callback = None
            self._run_callback(callback, self._consume(num_bytes))
            return True
        elif self._read_delimiter is not None:
            if self._read_buffer:
                while True:
                    loc = self._read_buffer[0].find(self._read_delimiter)
                    if loc != -1:
                        callback = self._read_callback
                        delimiter_len = len(self._read_delimiter)
                        self._read_delimiter = None
                        self._read_callback = None
                        self._run_callback(callback,
                                           self._consume(loc + delimiter_len))
                        return True
                    if len(self._read_buffer) == 1:
                        break
                    _double_prefix(self._read_buffer)
        return False

    def _run_callback(self, callback, *args):
        def wrapper():
            try:
                callback(*args)
            except:
                print('iostream._run_callback exception.')
                self.close()
                raise
            self._maybe_add_error_listener()
        self._io_loop.add_callback(wrapper)
            

    def _consume(self, loc):
        if loc == 0:
            return b''
        _merge_prefix(self._read_buffer, loc)
        self._read_buffer_size -= loc
        return self._read_buffer.popleft()

        
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


def _double_prefix(deque):
    new_len = max(len(deque[0]) * 2,
                  len(deque[0]) + len(deque[1]))
    _merge_prefix(deque, new_len)

def _merge_prefix(deque, size):
    if len(deque) == 1 and len(deque[0]) <= size:
        return
    remaining = size
    prefix = []
    while deque and remaining:
        chunk = deque.popleft()
        if len(chunk) > remaining:
            deque.appendleft(chunk[remaining:])
            chunk = chunk[:remaining]
        prefix.append(chunk)
        remaining -= len(chunk)
    if prefix:
        deque.appendleft(type(prefix[0])().join(prefix))
    else:
        deque.appendleft(b'')
