#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: epoll.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 10:40:03>

import select

from ioloop import PollIOLoop

class EPollIOLoop(PollIOLoop):
    def initialize(self, **kwargs):
        super(EPollIOLoop, self).initialize(impl=select.epoll(), **kwargs)

if __name__ == '__main__':
    e = EPollIOLoop()
    print(dir(e))

