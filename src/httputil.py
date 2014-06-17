#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: httputil.py
# Author:   Chenbin
# Time-stamp: <2014-06-17 Tue 16:57:51>

class HTTPHeader(dict):
    def __init__(self, *args, **kwargs):
        super(HTTPHeader, self).__init__(self)

    def parse_line(self, line):
        name, value = line.strip().split(':', 1)
        self[name] = value.strip()

    def get(self, name, default=None):
        return dict.get(self, name, default)

    @classmethod
    def parse(cls, headers):
        h = cls()
        for line in headers.splitlines():
            if line:
                h.parse_line(line)
        return h


if __name__ == '__main__':
    h = HTTPHeader.parse('Content-Type: text/html\r\nContent-Length: 42\r\n')
    print(h.get('Content-Type'))
        
