#!/usr/bin/env python

import sys
import os
from base_module import Base_check

class Get_conf:

    def __init__(self, args):
        self.args = args
        self.conf = dict()

    def _parse_config(self):
        '''Parse config file for module_name'''
        path = os.path.dirname(sys.argv[0]) + '/modules/mon_conf.d/' + self.args.module
        if os.path.isfile(path):
            with open(path) as file:
                for line in file:
                    if line and len(line.split('=')) == 2:
                        key = line.split('=')[0].strip()
                        val = line.split('=')[1].strip()
                        self.conf[key] = val

    def _parse_args(self):
        '''Parse config options from args'''
        if self.args.conf:
            for line in self.args.conf:
                line = line.split('=')
                self.conf[line[0]] = line[1]

    def run(self):
        self._parse_config()
        self._parse_args()
        return self.conf
