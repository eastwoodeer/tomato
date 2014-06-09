#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: ioloop.py
# Author:   Chenbin
# Time-stamp: <2014-06-09 Mon 15:23:20>

import threading

from util import Configurable

class IOLoop(Configurable):
    # Constants from the epoll module
    _EPOLLIN = 0x001
    _EPOLLPRI = 0x002
    _EPOLLOUT = 0x004
    _EPOLLERR = 0x008
    _EPOLLHUP = 0x010
    _EPOLLRDHUP = 0x2000
    _EPOLLONESHOT = (1 << 30)
    _EPOLLET = (1 << 31)
                                        
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP

    _instance_lock = threading.Lock()
    _current = threading.local()

    @staticmethod
    def instance():
        if not hasattr(IOLoop, '_instance'):
            with IOLoop._instance_lock:
                if not hasattr(IOLoop, '_instance'):
                    IOLoop._instance = IOLoop()
        return IOLoop._instance

    @staticmethod
    def current():
        current = getattr(IOLoop._current, 'instance', None)
        if current is None:
            return IOLoop.instance()
        return current

    @classmethod
    def configurable_base(cls):
        return IOLoop

    @classmethod
    def configurable_default(cls):
        from epoll import EPollIOLoop
        return EPollIOLoop

    def add_handler(self, fd, handler, events):
        raise NotImplementedError()

    def remove_handler(self, fd):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()


_POLL_TIMEOUT = 3600.0

class PollIOLoop(IOLoop):
    def initialize(self, impl):
        self._impl = impl
        self._events = {}
        self._handlers = {}

    def add_handler(self, fd, handler, events):
        self._handlers[fd] = handler
        self._impl.register(fd, events | self.ERROR)

    def remove_handler(self, fd):
        self._handlers.pop(fd, None)
        self._events.pop(fd, None)
        try:
            self._impl.unregister(fd)
        except Exception as e:
            print("error delete fd from ioloop...", e)

    def start(self):
        poll_timeout = _POLL_TIMEOUT
        old_current = getattr(IOLoop._current, 'instance', None)
        IOLoop._current.instance = self
        try:
            while True:
                try:
                    event_pairs = self._impl.poll(poll_timeout)
                except Exception as e:
                    print('error: ', e)
                    break

                self._events.update(event_pairs)
                while self._events:
                    fd, events = self._events.popitem()
                    self._handlers[fd](fd, events)
                    # try:
                    #     self._handlers[fd](fd, events)
                    # except Exception as e:
                    #     print('handlers exception...', e)
        finally:
            IOLoop._current.instance = old_current
            print('end of the world')


if __name__ == '__main__':
    p = IOLoop()
    print(hasattr(p, 'instance'))
    q = IOLoop.instance()
    print(hasattr(q, 'instance'))

    print(hasattr(IOLoop._current, 'instance'))
