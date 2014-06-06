#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: netutil.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 11:11:32>

import socket
import errno

from ioloop import IOLoop
from epoll import EPollIOLoop

def add_accept_handler(sock, callback, io_loop=None):
    if io_loop is None:
        io_loop = IOLoop.current()

    def accept_handler(fd, events):
        while True:
            try:
                connection, address = sock.accept()
            except socket.error as e:
                if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    return
                if e.args[0] == errno.ECONNABORTED:
                    continue
                raise
            callback(connection, address)
    io_loop.add_handler(sock.fileno(), accept_handler, IOLoop.READ)

def bind_sockets(port, address=None, family=socket.AF_UNSPEC, backlog=128, flags=None):
    sockets = []
    if address == '':
        address = None
    if not socket.has_ipv6 and family == socket.AF_UNSPEC:
        family = socket.AF_INET

    if flags is None:
        flags = socket.AI_PASSIVE
    for res in set(socket.getaddrinfo(address, port, family, socket.SOCK_STREAM, 0, flags)):
        af, socktype, proto, canonname, sockaddr = res
        try:
            sock = socket.socket(af, socktype, proto)
        except socket.error as e:
            print(e)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if af == socket.AF_INET6:
            if hasattr(socket, 'IPPROTO_IPV6'):
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        sock.setblocking(0)
        sock.bind(sockaddr)
        sock.listen(backlog)
        sockets.append(sock)
    return sockets
        
