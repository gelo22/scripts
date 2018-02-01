#!/usr/bin/env python

from core.base_module import Base_check

class Check(Base_check):

    def __init__(self, args):
        '''Get agrguments, get data from module's config and command line arguments'''
        self.args = args
        self._get_conf()

    def _example(self):
        '''Our example check'''
        key = 'example_key'
        value = 123
        self.sender_data[key] = value

    def run(self):
        self._example()
        self._send()

