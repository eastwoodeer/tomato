#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# Filename: util.py
# Author:   Chenbin
# Time-stamp: <2014-06-06 Fri 10:44:17>

class Configurable(object):
    def __new__(cls, **kwargs):
        base = cls.configurable_base()
        args = {}

        if cls is base:
            impl = cls.configurable_default()
        else:
            impl = cls
        args.update(kwargs)
        instance = super(Configurable, cls).__new__(impl)
        instance.initialize(**args)
        return instance

    @classmethod
    def configurable_base(cls):
        raise NotImplementedError()

    @classmethod
    def configurable_default(cls):
        raise NotImplementedError()
