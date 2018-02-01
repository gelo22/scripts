#!/usr/bin/env python

from core.base_module import Base_check

class Check(Base_check):

    def __init__(self, args):
        self.args = args
        self._get_conf()
        self.meminfo_path = self.conf['meminfo_file']

    def _parse_meminfo(self):
        '''Parse meminfo'''
        with open(self.meminfo_path) as mfile:
            for line in mfile:
                if line.startswith('Mem'):
                    line = line.split()
                    key = line[0][:-1]
                    val = line[1]
                    self.sender_data[key] = val

    def run(self):
#       for key in self.conf:
#           print key, self.conf[key]
        self._parse_meminfo()
        self._send()

