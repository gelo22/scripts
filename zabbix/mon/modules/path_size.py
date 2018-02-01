#!/usr/bin/env python

import glob
from subprocess import Popen, PIPE
from core.base_module import Base_check

import time

class Check(Base_check):

    def __init__(self, args):
        '''Get agrguments, get data from module's config and command line arguments'''
        self.args = args
        self._get_conf()
        self.files = glob.glob(self.conf['path'] + '*')

    def _check_space(self):
        '''Check space usage in directory'''
        args = ['/usr/bin/du', '-sb', '']
        for path in self.files:
            args[len(args) - 1] = path
            proc0 = Popen(args, stdout=PIPE, stderr=PIPE)
            for line in proc0.stdout:
                line = line.split()
                key = line[1]
                value = line[0]
                self.sender_data[key] = value

    def run(self):
        self._check_space()
        self._send()

